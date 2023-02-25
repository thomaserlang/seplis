import api from '@seplis/api'
import Player, { IPlayNextProps } from '@seplis/components/player/player'
import { IEpisode } from '@seplis/interfaces/episode'
import { IPlaySourceStream } from '@seplis/interfaces/play-server'
import { ISeries, ISeriesUserSettings } from '@seplis/interfaces/series'
import { episodeTitle } from '@seplis/utils'
import { useQuery } from '@tanstack/react-query'
import { useRef } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'


export default function PlayEpisode() {
    const { seriesId, episodeNumber } = useParams()
    const navigate = useNavigate()
    const location = useLocation()

    const episode = useQuery(['episode-title-watched', seriesId, episodeNumber], async () => {
        const result = await Promise.all([
            api.get<ISeries>(`/2/series/${seriesId}`),
            api.get<IEpisode>(`/2/series/${seriesId}/episodes/${episodeNumber}`, {
                params: {
                    expand: 'user_watched',
                }
            }),
            api.get<ISeriesUserSettings>(`/2/series/${seriesId}/user-settings`),
        ])
        return {
            title: `${result[0].data.title} ${episodeTitle(result[1].data)}`,
            startTime: result[1].data.user_watched?.position ?? 0,
            audioLang: result[2].data?.audio_lang,
            subtitleLang: result[2].data?.subtitle_lang,
        }
    })

    const playNext = useQuery<IPlayNextProps>(['episode-play-next', seriesId, episodeNumber], async () => {
        const result = await api.get<IEpisode>(`/2/series/${seriesId}/episodes/${parseInt(episodeNumber) + 1}`, {
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
        const watched = (((time / 100) * 10) > (duration - time))
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

    const onAudioChange = (source: IPlaySourceStream) => {
        api.put(`/2/series/${seriesId}/user-settings`, {
            'audio_lang': source ? `${source.language || source.title}:${source.index}` : null,
        })
    }
    const onSubtitleChange = (source: IPlaySourceStream) => {
        api.put(`/2/series/${seriesId}/user-settings`, {
            'subtitle_lang': source ? `${source.language || source.title}:${source.index}` : null,
        })
    }

    return <Player
        getPlayServersUrl={`/2/series/${seriesId}/episodes/${episodeNumber}/play-servers`}
        title={episode.data?.title}
        startTime={episode.data?.startTime}
        playNext={playNext?.data}
        onTimeUpdate={onTimeUpdate}
        loading={episode.isLoading}
        defaultAudio={episode.data?.audioLang}
        defaultSubtitle={episode.data?.subtitleLang}
        onAudioChange={onAudioChange}
        onSubtitleChange={onSubtitleChange}
        onClose={() => {
            if (location.key && location.key != 'default')
                navigate(-1)
            else
                navigate(`/series/${seriesId}`)
        }}
    />
}