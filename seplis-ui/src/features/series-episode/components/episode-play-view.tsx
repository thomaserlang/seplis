import { PlayerContainer } from '@/features/play'
import { useGetEpisodePlayRequests } from '../api/episode-play-requests.api'

interface Props {
    seriesId: number
    episodeNumber: number
    title?: string
    subtitle?: string
    onClose?: () => void
}

export function EpisodePlayView({
    seriesId,
    episodeNumber,
    title,
    subtitle,
    onClose,
}: Props) {
    const { data, isLoading } = useGetEpisodePlayRequests({
        seriesId,
        episodeNumber,
    })

    return (
        <PlayerContainer
            playRequests={data || []}
            title={title}
            subtitle={subtitle}
            onClose={onClose}
        />
    )
}
