import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { PlayerContainer } from '@/features/play'
import { useGetMoviePlayRequests } from '../api/movie-play-requests.api'
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

    if (movie.isLoading || playRequests.isLoading) return <PageLoader />
    if (movie.error) return <ErrorBox errorObj={movie.error} />
    if (playRequests.error) return <ErrorBox errorObj={playRequests.error} />
    if (!movie.data) return <ErrorBox message="Movie not found" />
    if (!playRequests.data)
        return <ErrorBox message="No playable sources found" />

    return (
        <PlayerContainer
            playRequests={playRequests.data}
            title={movie.data.title ?? undefined}
            onClose={onClose}
        />
    )
}
