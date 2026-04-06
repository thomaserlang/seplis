import { PlayerContainer } from '@/features/play'
import { useGetMoviePlayRequests } from '../api/movie-play-requests.api'

interface Props {
    movieId: number
    title?: string
    onClose?: () => void
}

export function MoviePlayView({ movieId, title, onClose }: Props) {
    const { data, isLoading } = useGetMoviePlayRequests({
        movieId,
    })

    return (
        <PlayerContainer
            playRequests={data ?? []}
            title={title}
            onClose={onClose}
        />
    )
}
