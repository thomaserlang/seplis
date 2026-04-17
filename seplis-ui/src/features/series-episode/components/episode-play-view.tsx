import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { PlayerContainer } from '@/features/play'
import {
    getSeries,
    getSeriesUserSettings,
    updateSeriesUserSettings,
} from '@/features/series'
import { useQuery } from '@tanstack/react-query'
import { isHTTPError } from 'ky'
import { useSearchParams } from 'react-router-dom'
import { getEpisodePlayRequests } from '../api/episode-play-requests.api'
import { updateEpisodeWatchedPosition } from '../api/episode-watched-position.api'
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
    const [_, setParams] = useSearchParams()
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
            return {
                series,
                episode,
                nextEpisode,
                playRequests,
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
        episodeWatched,
        userSettings,
    } = data.data || {}

    if (!series) return <ErrorBox message="Series not found" />
    if (!episode) return <ErrorBox message="Episode not found" />
    if (!playRequests) return <ErrorBox message="No playable requests found" />

    const title = series.title || 'Unknown Title'
    const secondaryTitle = `S${episode.season} E${episode.episode}${episode?.title ? ` - ${episode?.title}` : ''}`

    return (
        <PlayerContainer
            playRequests={playRequests}
            title={title}
            secondaryTitle={secondaryTitle}
            onClose={onClose}
            onPlayNext={
                nextEpisode
                    ? () =>
                          setParams((params) => {
                              params.set(
                                  'pid',
                                  `episode-${seriesId}:${nextEpisode.number}`,
                              )
                              return params
                          })
                    : undefined
            }
            defaultStartTime={episodeWatched?.position ?? 0}
            defaultAudio={userSettings?.audio_lang ?? undefined}
            defaultSubtitle={userSettings?.subtitle_lang ?? undefined}
            onSavePosition={(position) =>
                updateEpisodeWatchedPosition({
                    seriesId,
                    episodeNumber,
                    data: {
                        position,
                    },
                })
            }
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
                        subtitle_lang: subtitle || null,
                    },
                })
            }}
            onAudioChange={(audio) => {
                updateSeriesUserSettings({
                    seriesId,
                    data: {
                        audio_lang: audio || null,
                    },
                })
            }}
        />
    )
}
