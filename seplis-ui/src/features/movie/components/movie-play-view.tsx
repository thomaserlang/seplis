import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { PlayerContainer } from '@/features/play'
import { useGetMoviePlayRequests } from '../api/movie-play-requests.api'
import { useUpdateMovieWatchedPosition } from '../api/movie-watched-position'
import {
    useGetMovieWatched,
    useIncrementMovieWatched,
} from '../api/movie-watched.api'
import { useGetMovie } from '../api/movie.api'

interface Props {
    movieId: number
    onClose?: () => void
}

export function MoviePlayView({ movieId, onClose }: Props) {
    const movie = useGetMovie({ movieId })
    const playRequests = useGetMoviePlayRequests({
        movieId,
    })
    const watchedPosition = useGetMovieWatched({ movieId })
    const updateWatchedPosition = useUpdateMovieWatchedPosition({})
    const incrementWatched = useIncrementMovieWatched({})

    const queries = [movie, playRequests, watchedPosition]
    if (queries.some((q) => q.isLoading)) return <PageLoader />

    const error = queries.find((q) => q.error)?.error
    if (error) return <ErrorBox errorObj={error} />
    if (!movie.data) return <ErrorBox message="Movie not found" />
    if (!playRequests.data)
        return <ErrorBox message="No playable sources found" />

    return (
        <PlayerContainer
            playRequests={playRequests.data}
            title={movie.data.title ?? undefined}
            onClose={onClose}
            defaultStartTime={watchedPosition.data?.position ?? 0}
            onSavePosition={(position) =>
                updateWatchedPosition.mutate({
                    movieId,
                    data: {
                        position,
                    },
                })
            }
            onFinished={() => {
                incrementWatched.mutate({ movieId })
            }}
        />
    )
}
