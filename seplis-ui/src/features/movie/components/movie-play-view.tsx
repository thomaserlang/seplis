import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { PlayerContainer } from '@/features/play'
import { useQuery } from '@tanstack/react-query'
import { getMoviePlayRequests } from '../api/movie-play-requests.api'
import { updateMovieWatchedPosition } from '../api/movie-watched-position'
import {
    getMovieWatched,
    incrementMovieWatched,
} from '../api/movie-watched.api'
import { getMovie } from '../api/movie.api'

interface Props {
    movieId: number
    onClose?: () => void
}

export function MoviePlayView({ movieId, onClose }: Props) {
    const data = useQuery({
        queryKey: ['movie-play-view', movieId],
        queryFn: async () => {
            const [movie, playRequests, watchedPosition] = await Promise.all([
                getMovie({ movieId }),
                getMoviePlayRequests({
                    movieId,
                }),
                getMovieWatched({
                    movieId,
                }),
            ])
            return {
                movie,
                playRequests,
                watchedPosition,
            }
        },
        refetchOnWindowFocus: false,
    })
    if (data.isLoading) return <PageLoader />

    if (data.error) return <ErrorBox errorObj={data.error} />
    const { movie, playRequests, watchedPosition } = data.data || {}

    if (!movie) return <ErrorBox message="Movie not found" />
    if (!playRequests) return <ErrorBox message="No playable sources found" />

    return (
        <PlayerContainer
            playRequests={playRequests}
            title={movie.title ?? undefined}
            onClose={onClose}
            defaultStartTime={watchedPosition?.position ?? 0}
            onSavePosition={(position) =>
                updateMovieWatchedPosition({
                    movieId,
                    data: {
                        position,
                    },
                })
            }
            onFinished={() => {
                incrementMovieWatched({ movieId })
            }}
        />
    )
}
