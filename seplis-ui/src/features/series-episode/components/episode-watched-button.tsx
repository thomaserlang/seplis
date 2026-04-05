import { WatchedButton } from '@/components/watched-button'
import { useActiveUser } from '@/features/user'
import { toastError } from '@/utils/toast'
import {
    useDecrementEpisodeWatched,
    useGetEpisodeWatched,
    useIncrementEpisodeWatched,
} from '../api/episode-watched.api'

interface Props {
    seriesId: number
    episodeId: number
    duration?: number | null
}

export function EpisodeWatchedButton({ seriesId, episodeId, duration }: Props) {
    const [user] = useActiveUser()
    const { data, isLoading } = useGetEpisodeWatched({
        seriesId,
        episodeId,
        options: {
            enabled: !!user,
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

    return (
        <WatchedButton
            times={data?.times ?? 0}
            position={data?.position ?? 0}
            duration={duration}
            loading={isLoading}
            onIncrement={() => increment.mutate({ seriesId, episodeId })}
            onDecrement={() => decrement.mutate({ seriesId, episodeId })}
        />
    )
}
