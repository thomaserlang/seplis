import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { getPlayRequestSources, PlayerContainer } from '@/features/play'
import { toLangKey } from '@/features/play/utils/play-source.utils'
import {
    getSeries,
    getSeriesUserSettings,
    updateSeriesUserSettings,
} from '@/features/series'
import { useQuery } from '@tanstack/react-query'
import { isHTTPError } from 'ky'
import { useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getEpisodePlayRequests } from '../api/episode-play-requests.api'
import {
    refetchEpisodeWatchedPositionSummaries,
    updateEpisodeWatchedPosition,
} from '../api/episode-watched-position.api'
import {
    getEpisodeWatched,
    incrementEpisodeWatched,
} from '../api/episode-watched.api'
import { getEpisode } from '../api/episode.api'

interface Props {
    seriesId: number
    episodeNumber: number
    onClose?: () => void
}

export function EpisodePlayView({ seriesId, episodeNumber, onClose }: Props) {
    const [params, setParams] = useSearchParams()
    const positionSavedRef = useRef(false)
    const pendingPositionSavesRef = useRef(new Set<Promise<void>>())
    const [urlPosition] = useState(() => {
        const urlPositionParam = params.get('position')
        if (urlPositionParam === null) return undefined

        const value = Number(urlPositionParam)
        return Number.isFinite(value) ? value : undefined
    })

    useEffect(() => {
        if (!params.has('position')) return

        setParams(
            (currentParams) => {
                const nextParams = new URLSearchParams(currentParams)
                nextParams.delete('position')
                return nextParams
            },
            { replace: true },
        )
    }, [params, setParams])

    useEffect(
        () => () => {
            if (!positionSavedRef.current) return

            const pendingSaves = [...pendingPositionSavesRef.current]
            void Promise.allSettled(pendingSaves).then(() =>
                refetchEpisodeWatchedPositionSummaries(seriesId),
            )
        },
        [seriesId],
    )

    const data = useQuery({
        queryKey: ['episode-play-view', seriesId, episodeNumber],
        queryFn: async () => {
            const [
                series,
                episode,
                nextEpisode,
                playRequests,
                episodeWatched,
                userSettings,
            ] = await Promise.all([
                getSeries({ seriesId }),
                getEpisode({ seriesId, episodeNumber }),
                getEpisode({
                    seriesId,
                    episodeNumber: episodeNumber + 1,
                }).catch((error) => {
                    if (isHTTPError(error) && error.response.status === 404) {
                        return null
                    }
                    throw error
                }),
                getEpisodePlayRequests({
                    seriesId,
                    episodeNumber,
                }),
                getEpisodeWatched({
                    seriesId,
                    episodeNumber,
                }),
                getSeriesUserSettings({ seriesId }),
            ])
            const nextPlayRequests = nextEpisode
                ? await getEpisodePlayRequests({
                      seriesId,
                      episodeNumber: nextEpisode.number,
                  })
                : []
            const nextPlayRequestSources = nextPlayRequests.length
                ? await getPlayRequestSources({
                      playRequests: nextPlayRequests,
                  })
                : []

            return {
                series,
                episode,
                nextEpisode,
                playRequests,
                nextPlayRequestSources,
                episodeWatched,
                userSettings,
            }
        },
        refetchOnWindowFocus: false,
    })

    if (data.isLoading) return <PageLoader />
    if (data.error) return <ErrorBox errorObj={data.error} />

    const {
        series,
        episode,
        nextEpisode,
        playRequests,
        nextPlayRequestSources,
        episodeWatched,
        userSettings,
    } = data.data || {}

    if (!series) return <ErrorBox message="Series not found" />
    if (!episode) return <ErrorBox message="Episode not found" />
    if (!playRequests) return <ErrorBox message="No playable requests found" />

    const title = series.title || 'Unknown Title'
    const secondaryTitle = `S${episode.season} E${episode.episode}${episode?.title ? ` - ${episode?.title}` : ''}`
    const canPlayNext = nextEpisode && nextPlayRequestSources?.length
    const startPosition =
        urlPosition !== undefined
            ? urlPosition
            : (episodeWatched?.position ?? 0)

    return (
        <PlayerContainer
            playRequests={playRequests}
            title={title}
            secondaryTitle={secondaryTitle}
            onClose={onClose}
            onPlayNext={
                canPlayNext
                    ? () =>
                          setParams((params) => {
                              params.set(
                                  'pid',
                                  `episode-${seriesId}:${nextEpisode.number}`,
                              )
                              params.set('position', '0')
                              return params
                          })
                    : undefined
            }
            defaultStartTime={startPosition}
            defaultAudioKey={userSettings?.audio_lang ?? undefined}
            defaultSubtitleKey={userSettings?.subtitle_lang ?? undefined}
            onSavePosition={(position) => {
                positionSavedRef.current = true
                const request = updateEpisodeWatchedPosition({
                    seriesId,
                    episodeNumber,
                    data: {
                        position,
                    },
                })
                pendingPositionSavesRef.current.add(request)
                void request.then(
                    () => pendingPositionSavesRef.current.delete(request),
                    () => pendingPositionSavesRef.current.delete(request),
                )
                return request
            }}
            onFinished={() => {
                incrementEpisodeWatched({ seriesId, episodeNumber })
            }}
            castInfo={{
                savePositionUrl: `${window.location.origin}/api/2/series/${seriesId}/episodes/${episodeNumber}/watched-position`,
                watchedUrl: `${window.location.origin}/api/2/series/${seriesId}/episodes/${episodeNumber}/watched`,
            }}
            onSubtitleChange={(subtitle) => {
                updateSeriesUserSettings({
                    seriesId,
                    data: {
                        subtitle_lang: toLangKey(subtitle) || null,
                    },
                })
            }}
            onAudioChange={(audio) => {
                updateSeriesUserSettings({
                    seriesId,
                    data: {
                        audio_lang: toLangKey(audio) || null,
                    },
                })
            }}
        />
    )
}
