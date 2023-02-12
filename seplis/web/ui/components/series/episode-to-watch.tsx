import { Box, Heading, Text } from '@chakra-ui/react'
import api from '@seplis/api'
import { IEpisode, IEventEpisodeWatched } from '@seplis/interfaces/episode'
import { EVENT_EPISODE_WATCHED, useEventListener } from '@seplis/events'
import { isAuthed } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import EpisodeCard from './episode-card'
import EpisodeSkeleton from './episode-card-skeleton'

export default function EpisodeToWatch({ seriesId }: { seriesId: number }) {
    if (!isAuthed())
        return null
    const { data, isInitialLoading, refetch } = useQuery(['series', seriesId, 'episode-to-watch'], async () => {
        const r = await api.get<IEpisode>(`/2/series/${seriesId}/episode-to-watch`)
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
            <Heading as="h2" fontSize="2xl" marginBottom="0.25rem">To watch</Heading>
            <EpisodeSkeleton />
        </Box>
    return <Box width="100%">
        <Heading as="h2" fontSize="2xl" marginBottom="0.25rem">To watch</Heading>
        {data && <EpisodeCard seriesId={seriesId} episode={data} />}
        {!data && <Text color="gray.400">No episodes to watch</Text>}
    </Box>
}