import { PlayerContainer } from '@/features/play'
import { useGetMoviePlayRequests } from '../api/movie-play-requests.api'

interface Props {
    movieId: number
}

export function MoviePlayView({ movieId }: Props) {
    const { data, isLoading } = useGetMoviePlayRequests({
        movieId,
    })

    return <PlayerContainer playRequests={data ?? []} />
}
