import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { PlayerContainer } from '@/features/play'
import { useGetSeries } from '@/features/series/api/series.api'
import { useGetEpisodePlayRequests } from '../api/episode-play-requests.api'
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

    if (series.isLoading || episode.isLoading || playRequests.isLoading)
        return <PageLoader />
    if (series.error) return <ErrorBox errorObj={series.error} />
    if (episode.error) return <ErrorBox errorObj={episode.error} />
    if (playRequests.error) return <ErrorBox errorObj={playRequests.error} />
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
        />
    )
}
