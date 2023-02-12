import { Flex } from '@chakra-ui/react'
import { GetAllCursor } from '@seplis/api'
import { IEpisode } from '@seplis/interfaces/episode'
import { ISeries } from '@seplis/interfaces/series'
import { isAuthed } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import EpisodeCard from './episode-card'
import SeasonSelect from './season-select'


interface IProps {
    series: ISeries
    defaultSeason?: number
}

export default function Episodes({ series, defaultSeason = 1 }: IProps) {
    const [season, setSeason] = useState(defaultSeason)
    return <>
        <SeasonSelect seasons={series.seasons} defaultSeason={defaultSeason} onSelect={setSeason} />
        <RenderEpisodes seriesId={series.id} season={season} />
    </>
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
        return <>Loading episodes</>

    return <Flex wrap="wrap" gap="0.5rem">
        {data.map(episode => (
            <Flex
                key={`episode-${episode.number}`}
                grow="1"
                basis="300px"
            >
                <EpisodeCard
                    seriesId={seriesId}
                    episode={episode}
                />
            </Flex>
        ))}
        <Flex height="0px" grow="1" basis="300px"></Flex>
        <Flex height="0px" grow="1" basis="300px"></Flex>
        <Flex height="0px" grow="1" basis="300px"></Flex>
    </Flex>
}