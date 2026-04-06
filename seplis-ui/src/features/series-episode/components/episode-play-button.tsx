import { PlayButton } from '@/features/play'
import { useActiveUser } from '@/features/user'
import { ButtonSize } from '@mantine/core'
import { useNavigate } from 'react-router-dom'
import { useGetEpisodePlayRequests } from '../api/episode-play-requests.api'

interface Props {
    seriesId: number
    episodeNumber: number
    canPlay?: boolean
    size?: ButtonSize
}

export function EpisodePlayButton({
    seriesId,
    episodeNumber,
    canPlay,
    size,
}: Props) {
    const [user] = useActiveUser()
    const navigate = useNavigate()
    const { data, isLoading, refetch } = useGetEpisodePlayRequests({
        seriesId,
        episodeNumber,
        options: {
            enabled: !!user && canPlay === undefined,
        },
    })

    return (
        <PlayButton
            playRequests={data}
            getPlayRequests={async () => {
                refetch()
            }}
            loading={isLoading}
            size={size}
            disabled={(!data || data.length === 0) && !canPlay}
            onClick={() => {
                navigate(`/series/${seriesId}/episodes/${episodeNumber}/play`)
            }}
        />
    )
}
