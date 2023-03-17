import { Flex, Heading, Text } from '@chakra-ui/react'
import api from '@seplis/api'
import { IEpisode, IEventEpisodeWatched } from '@seplis/interfaces/episode'
import { EVENT_EPISODE_WATCHED, useEventListener } from '@seplis/events'
import { isAuthed } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import EpisodeCard, { EpisodeCardWrapper } from './episode-card'
import EpisodeSkeleton from './episode-card-skeleton'

export default function EpisodeToWatch({ seriesId }: { seriesId: number }) {
    const { data, isInitialLoading, refetch } = useQuery(['series', seriesId, 'episode-to-watch'], async () => {
        const r = await api.get<IEpisode>(`/2/series/${seriesId}/episode-to-watch`)
        return r.data
    }, {
        refetchOnWindowFocus: true,
        enabled: isAuthed(),
    })

    useEventListener<IEventEpisodeWatched>(EVENT_EPISODE_WATCHED, ((data) => {
        if (data.seriesId == seriesId)
            refetch()
    }), [])

    return <Flex width="100%" direction="column">
        <Heading fontWeight="600" fontSize="2xl" marginBottom="0.25rem">To watch</Heading>
        {isInitialLoading ? <EpisodeSkeleton /> : <>
            {data && <EpisodeCard seriesId={seriesId} episode={data} />}
            {!data && <EpisodeCardWrapper><Text color="gray.400">No episodes to watch</Text></EpisodeCardWrapper>}
        </>}
    </Flex>
}