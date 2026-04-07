import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { PlayerContainer } from '@/features/play'
import {
    useGetSeries,
    useGetSeriesUserSettings,
    useUpdateSeriesUserSettings,
} from '@/features/series'
import { useGetEpisodePlayRequests } from '../api/episode-play-requests.api'
import { useUpdateEpisodeWatchedPosition } from '../api/episode-watched-position'
import {
    useGetEpisodeWatched,
    useIncrementEpisodeWatched,
} from '../api/episode-watched.api'
import { useGetEpisode } from '../api/episode.api'

interface Props {
    seriesId: number
    episodeNumber: number
    onClose?: () => void
}

export function EpisodePlayView({ seriesId, episodeNumber, onClose }: Props) {
    const series = useGetSeries({ seriesId })
    const episode = useGetEpisode({ seriesId, episodeNumber })
    const playRequests = useGetEpisodePlayRequests({
        seriesId,
        episodeNumber,
    })
    const episodeWatched = useGetEpisodeWatched({
        seriesId,
        episodeNumber,
    })
    const userSettings = useGetSeriesUserSettings({ seriesId })
    const updateUserSettings = useUpdateSeriesUserSettings({})
    const updateWatchedPosition = useUpdateEpisodeWatchedPosition({})
    const incrementWatched = useIncrementEpisodeWatched({})

    const queries = [
        series,
        episode,
        playRequests,
        episodeWatched,
        userSettings,
    ]
    if (queries.some((q) => q.isLoading)) return <PageLoader />

    const error = queries.find((q) => q.error)?.error
    if (error) return <ErrorBox errorObj={error} />

    if (!series.data) return <ErrorBox message="Series not found" />
    if (!episode.data) return <ErrorBox message="Episode not found" />
    if (!playRequests.data)
        return <ErrorBox message="No playable requests found" />

    const title = series.data?.title ?? undefined
    const secondaryTitle = episode.data
        ? `S${episode.data.season} E${episode.data.episode}${episode.data.title ? ` - ${episode.data.title}` : ''}`
        : undefined

    return (
        <PlayerContainer
            playRequests={playRequests.data}
            title={title}
            secondaryTitle={secondaryTitle}
            onClose={onClose}
            defaultStartTime={episodeWatched.data?.position ?? 0}
            defaultAudio={userSettings.data?.audio_lang ?? undefined}
            defaultSubtitle={userSettings.data?.subtitle_lang ?? undefined}
            onSavePosition={(position) =>
                updateWatchedPosition.mutate({
                    seriesId,
                    episodeNumber,
                    data: {
                        position,
                    },
                })
            }
            onFinished={() => {
                incrementWatched.mutate({ seriesId, episodeNumber })
            }}
            onSubtitleChange={(subtitle) => {
                updateUserSettings.mutate({
                    seriesId,
                    data: {
                        subtitle_lang: subtitle || null,
                    },
                })
            }}
            onAudioChange={(audio) => {
                updateUserSettings.mutate({
                    seriesId,
                    data: {
                        audio_lang: audio || null,
                    },
                })
            }}
        />
    )
}
