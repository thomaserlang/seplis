import { Text } from '@chakra-ui/react'
import api from '@seplis/api'
import { IEpisode } from '@seplis/interfaces/episode'
import { IPageCursorResult } from '@seplis/interfaces/page'
import { dateInDays, episodeNumber } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'


export default function EpisodeNextToAir({ seriesId }: { seriesId: number }) {
    const { data } = useQuery<IEpisode>(['series', seriesId, 'episode-next-to-air'], async () => {
        const r = await api.get<IPageCursorResult<IEpisode>>(`/2/series/${seriesId}/episodes`, {
            params: {
                'air_date_ge': new Date().toISOString().substring(0, 10),
                'first': 1,
            }
        })
        if (r.data.items.length >= 1)
            return r.data.items[0]
        else
            return null
    })
    if (!data)
        return
    return <Text>Next episode: {episodeNumber(data)} - {data.title}{countdown(data.air_datetime)}</Text>
}


function countdown(air_datetime: string) {
    if (!air_datetime)
        return ''
    const m = (new Date(air_datetime).getTime() - new Date().getTime())
    if (m > 0)
        return <>, in <span title={air_datetime}>{dateInDays(air_datetime)}</span></>
    return <>, <span title={air_datetime}>{dateInDays(air_datetime)}</span> ago</>
}