import { PlayButton } from '@/features/play'
import { useActiveUser } from '@/features/user'
import { ButtonSize } from '@mantine/core'
import { useSearchParams } from 'react-router-dom'
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
    const [_, setParams] = useSearchParams()
    const [user] = useActiveUser()
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
                setParams((params) => {
                    params.set('pid', `episode-${seriesId}:${episodeNumber}`)
                    return params
                })
            }}
        />
    )
}
