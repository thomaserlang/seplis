import api from '@seplis/api'
import Player, { IPlayNextProps } from '@seplis/components/player/player'
import { IEpisode } from '@seplis/interfaces/episode'
import { ISeries } from '@seplis/interfaces/series'
import { episodeTitle } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'


export default function PlayEpisode() {
    const { seriesId, episodeNumber } = useParams()
    const title = useQuery(['episode-title', seriesId, episodeNumber], async () => {
        const result = await Promise.all([ 
            api.get<ISeries>(`/2/series/${seriesId}`),
            api.get<IEpisode>(`/2/series/${seriesId}/episodes/${episodeNumber}`),
        ])
        return `${result[0].data.title} ${episodeTitle(result[1].data)}`
    })
    const playNext = useQuery<IPlayNextProps>(['episode-play-next', seriesId, episodeNumber], async () => {
        const result = await api.get<IEpisode>(`/2/series/${seriesId}/episodes/${parseInt(episodeNumber)+1}`, {
            params: {
                'expand': 'user_can_watch',
            }
        })
        if (result.data && result.data.user_can_watch.on_play_server) 
            return {
                title: episodeTitle(result.data),
                url: `/series/${seriesId}/episodes/${result.data.number}/play`
            }
        return null
    })

    return <Player 
        getPlayServersUrl={`/2/series/${seriesId}/episodes/${episodeNumber}/play-servers`}
        title={title?.data}
        startTime={0}
        playNext={playNext?.data}
    />
}