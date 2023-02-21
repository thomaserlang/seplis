import api from '@seplis/api'
import Player, { IPlayNextProps } from '@seplis/components/player/player'
import { IEpisode } from '@seplis/interfaces/episode'
import { ISeries } from '@seplis/interfaces/series'
import { episodeTitle } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import { useRef } from 'react'
import { useParams } from 'react-router-dom'


export default function PlayEpisode() {
    const { seriesId, episodeNumber } = useParams()

    const episode = useQuery(['episode-title-watched', seriesId, episodeNumber], async () => {
        const result = await Promise.all([ 
            api.get<ISeries>(`/2/series/${seriesId}`),
            api.get<IEpisode>(`/2/series/${seriesId}/episodes/${episodeNumber}`, {
                params: {
                    expand: 'user_watched',
                }
            }),
        ])
        return {
            title: `${result[0].data.title} ${episodeTitle(result[1].data)}`,
            startTime: result[1].data.user_watched?.position ?? 0,
        }
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

    const markedAsWatched = useRef(false)
    const prevSavedPosition = useRef(0)
    const onTimeUpdate = (time: number, duration: number) => {
        if ((time === episode.data.startTime) || (time === prevSavedPosition.current) || (time < 10) || ((time % 10) != 0))
            return
        const watched = (((time / 100) * 10) > (duration-time))
        prevSavedPosition.current = time
        if (watched) {
            if (!markedAsWatched.current) {             
                markedAsWatched.current = true
                api.post(`/2/series/${seriesId}/episodes/${episodeNumber}/watched`).catch(() => {
                    markedAsWatched.current = false
                })
            }
        } else {
            markedAsWatched.current = false
            api.put(`/2/series/${seriesId}/episodes/${episodeNumber}/watched-position`, {
                position: time
            })
        }
    }

    return <Player 
        getPlayServersUrl={`/2/series/${seriesId}/episodes/${episodeNumber}/play-servers`}
        title={episode.data?.title}
        startTime={episode.data?.startTime}
        playNext={playNext?.data}
        onTimeUpdate={onTimeUpdate}
        loading={episode.isLoading}
    />
}