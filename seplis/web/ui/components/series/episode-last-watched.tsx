import { Box, Text, Heading } from '@chakra-ui/react'
import api from '@seplis/api'
import { IEpisode, IEventEpisodeWatched } from '@seplis/interfaces/episode'
import { EVENT_EPISODE_WATCHED, useEventListener } from '@seplis/events'
import { isAuthed } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import EpisodeCard from './episode-card'
import EpisodeSkeleton from './episode-card-skeleton'

export default function EpisodeLastWatched({ seriesId }: { seriesId: number }) {
    if (!isAuthed())
        return null
    const { data, isInitialLoading, refetch } = useQuery(['series', seriesId, 'episode-last-watched'], async () => {
        const r = await api.get<IEpisode>(`/2/series/${seriesId}/episode-last-watched`)
        return r.data
    }, {
        refetchOnWindowFocus: true,
    })
    
    useEventListener<IEventEpisodeWatched>(EVENT_EPISODE_WATCHED, ((data) => {
        if (data.seriesId == seriesId)
            refetch()
    }), [])

    if (isInitialLoading)
        return <Box width="100%">    
            <Heading fontWeight="600" fontSize="2xl" marginBottom="0.25rem">Previously watched</Heading>
            <EpisodeSkeleton />
        </Box>
    return <Box width="100%">
        <Heading fontWeight="600" fontSize="2xl" marginBottom="0.25rem">Previously watched</Heading>
        {data && <EpisodeCard seriesId={seriesId} episode={data} />}
        {!data && <Text color="gray.400">You haven't watched an episode yet</Text>}
    </Box>
}