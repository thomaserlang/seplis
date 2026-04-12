import { WatchedButton, WatchedButtonProps } from '@/components/watched-button'
import { useActiveUser } from '@/features/user'
import { toastError } from '@/utils/toast'
import {
    useDecrementMovieWatched,
    useGetMovieWatched,
    useIncrementMovieWatched,
} from '../api/movie-watched.api'

interface Props extends WatchedButtonProps {
    movieId: number
}

export function MovieWatchedButton({ movieId, ...props }: Props) {
    const [user] = useActiveUser()
    const { data, isLoading } = useGetMovieWatched({
        movieId,
        options: {
            enabled: !!user,
        },
    })
    const increment = useIncrementMovieWatched({
        onError: (e) => {
            toastError(e)
        },
    })
    const decrement = useDecrementMovieWatched({
        onError: (e) => {
            toastError(e)
        },
    })

    return (
        <WatchedButton
            times={data?.times ?? 0}
            position={data?.position ?? 0}
            loading={isLoading}
            onIncrement={() => increment.mutate({ movieId })}
            onDecrement={() => decrement.mutate({ movieId })}
            {...props}
        />
    )
}
