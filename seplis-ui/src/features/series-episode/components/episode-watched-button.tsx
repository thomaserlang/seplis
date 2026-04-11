import { WatchedButton } from '@/components/watched-button'
import { useActiveUser } from '@/features/user'
import { toastError } from '@/utils/toast'
import { ButtonSize } from '@mantine/core'
import {
    useDecrementEpisodeWatched,
    useGetEpisodeWatched,
    useIncrementEpisodeWatched,
} from '../api/episode-watched.api'
import { Episode } from '../types/episode.types'

interface Props {
    seriesId: number
    episodeNumber: number
    episode?: Episode
    size?: ButtonSize
}

export function EpisodeWatchedButton({
    seriesId,
    episodeNumber,
    episode,
    size,
}: Props) {
    const [user] = useActiveUser()
    const { data, isLoading } = useGetEpisodeWatched({
        seriesId,
        episodeNumber,
        options: {
            enabled: !!user && episode?.user_watched === undefined,
        },
    })
    const increment = useIncrementEpisodeWatched({
        onError: (e) => {
            toastError(e)
        },
    })
    const decrement = useDecrementEpisodeWatched({
        onError: (e) => {
            toastError(e)
        },
    })

    const watchedData = data ?? episode?.user_watched

    return (
        <WatchedButton
            times={watchedData?.times ?? 0}
            position={watchedData?.position ?? 0}
            duration={episode?.runtime ?? 0}
            loading={isLoading}
            size={size}
            onIncrement={() =>
                increment.mutate({ seriesId, episodeNumber: episodeNumber })
            }
            onDecrement={() =>
                decrement.mutate({ seriesId, episodeNumber: episodeNumber })
            }
        />
    )
}
