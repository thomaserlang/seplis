import { PlayerContainer } from '@/features/play'
import { useGetEpisodePlayRequests } from '../api/episode-play-requests.api'

interface Props {
    seriesId: number
    episodeNumber: number
}

export function EpisodePlayView({ seriesId, episodeNumber }: Props) {
    const { data, isLoading } = useGetEpisodePlayRequests({
        seriesId,
        episodeNumber,
    })

    return <PlayerContainer playRequests={data || []} />
}
