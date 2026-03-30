import api from '@/api'
import { IEpisode } from '@/interfaces/episode'
import { IPageCursorResult } from '@/interfaces/page'
import { dateCountdown, episodeNumber } from '@/utils'
import { Text } from '@chakra-ui/react'
import { useQuery } from '@tanstack/react-query'

export default function EpisodeNextToAir({ seriesId }: { seriesId: number }) {
    const { data } = useQuery<IEpisode | undefined>(
        ['series', seriesId, 'episode-next-to-air'],
        async () => {
            const r = await api.get<IPageCursorResult<IEpisode>>(
                `/2/series/${seriesId}/episodes`,
                {
                    params: {
                        air_date_ge: new Date().toISOString().substring(0, 10),
                        first: 1,
                    },
                },
            )
            if (r.data.items.length >= 1) return r.data.items[0]
            return undefined
        },
    )
    if (!data) return
    return (
        <Text>
            Next episode: {episodeNumber(data)} - {data.title}
            {countdown(data.air_datetime ?? '')}
        </Text>
    )
}

function countdown(air_datetime: string) {
    if (!air_datetime) return ''
    return <>, {dateCountdown(air_datetime)}</>
}
