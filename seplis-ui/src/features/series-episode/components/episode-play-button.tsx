import { PlayButton } from '@/features/play'
import { ButtonSize } from '@mantine/core'
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
    const { data, isLoading, refetch } = useGetEpisodePlayRequests({
        seriesId,
        episodeNumber,
        options: {
            enabled: canPlay === undefined,
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
        />
    )
}
