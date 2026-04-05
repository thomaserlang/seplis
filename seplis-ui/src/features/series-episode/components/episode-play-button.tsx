import { PlayButton } from '@/features/play'
import { useGetEpisodePlayRequests } from '../api/episode-play-requests.api'

interface Props {
    seriesId: number
    episodeNumber: number
}

export function EpisodePlayButton({ seriesId, episodeNumber }: Props) {
    const { data, isLoading } = useGetEpisodePlayRequests({
        seriesId,
        episodeNumber,
    })
    return (
        data && (
            <PlayButton
                playRequests={data ?? []}
                loading={isLoading}
                disabled={!data || data.length === 0}
            />
        )
    )
}
