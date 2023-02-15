import { Flex, Stack, Wrap, WrapItem } from '@chakra-ui/react'
import { GetAllCursor } from '@seplis/api'
import { IEpisode } from '@seplis/interfaces/episode'
import { ISeries } from '@seplis/interfaces/series'
import { isAuthed } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import EpisodeCard from './episode-card'
import EpisodeSkeleton from './episode-card-skeleton'
import SeasonSelect from './season-select'


interface IProps {
    series: ISeries
    defaultSeason?: number
}

export default function Episodes({ series, defaultSeason = 1 }: IProps) {
    const [season, setSeason] = useState(defaultSeason)
    useEffect(() => {
        setSeason(defaultSeason)
    }, [series.id])
    return <Stack>
        <SeasonSelect seasons={series.seasons} season={season} onSelect={setSeason} />
        <RenderEpisodes seriesId={series.id} season={season} />
    </Stack>
}


export function RenderEpisodes({ seriesId, season }: { seriesId: number, season?: number }) {
    const { data, isInitialLoading } = useQuery(['series', seriesId, 'episodes', season], async () => {
        const result = await GetAllCursor<IEpisode>(`/2/series/${seriesId}/episodes`, {
            params: {
                'expand': isAuthed() ? 'user_watched,user_can_watch' : null,
                'season': season ? season : null,
                'first': 100,
            }
        })
        return result
    })

    if (isInitialLoading)
        return <LoadingEpisodes />

    return <Wrap>
        {data.map(episode => (
            <Flex key={`episode-${episode.number}`} grow="1" basis="300px"><WrapItem width="100%"><EpisodeCard
                seriesId={seriesId}
                episode={episode}
            /></WrapItem></Flex>
        ))}
        <Flex height="0px" grow="1" basis="300px"><WrapItem width="100%"></WrapItem></Flex>
        <Flex height="0px" grow="1" basis="300px"><WrapItem width="100%"></WrapItem></Flex>
        <Flex height="0px" grow="1" basis="300px"><WrapItem width="100%"></WrapItem></Flex>
    </Wrap>
}


export function LoadingEpisodes({ number = 6 }: { number?: number }) {
    return <>
        <Wrap>
            {[...Array(number)].map((_, i) => (
                <Flex key={i} grow="1" basis="300px"><WrapItem width="100%"><EpisodeSkeleton /></WrapItem></Flex>
            ))}
        </Wrap>
    </>
}
