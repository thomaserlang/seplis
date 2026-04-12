import {
    WatchlistButton,
    WatchlistButtonProps,
} from '@/components/watchlist-button'
import { useActiveUser } from '@/features/user/api/active-user.api'
import { toastError } from '@/utils/toast'
import {
    useCreateMovieWatchlist,
    useDeleteMovieWatchlist,
    useGetMovieWatchlist,
} from '../api/movie-watchlist.api'

interface Props extends WatchlistButtonProps {
    movieId: number
}

export function MovieWatchlistButton({ movieId, ...props }: Props) {
    const [user] = useActiveUser()
    const create = useCreateMovieWatchlist({
        onError: (e) => {
            toastError(e)
        },
    })
    const deleteWatchlist = useDeleteMovieWatchlist({
        onError: (e) => {
            toastError(e)
        },
    })
    const { data, isLoading } = useGetMovieWatchlist({
        movieId,
        options: {
            enabled: !!user,
        },
    })

    const toggleWatchlist = () => {
        if (data?.on_watchlist) {
            deleteWatchlist.mutate({
                movieId,
            })
        } else {
            create.mutate({
                movieId,
            })
        }
    }

    return (
        <WatchlistButton
            active={!!data?.on_watchlist}
            loading={isLoading || create.isPending || deleteWatchlist.isPending}
            onClick={() => {
                toggleWatchlist()
            }}
            {...props}
        />
    )
}
