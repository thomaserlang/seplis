import { PlayButton } from '@/features/play'
import { useGetMoviePlayRequests } from '../api/movie-play-requests.api'

interface Props {
    movieId: number
}

export function MoviePlayButton({ movieId }: Props) {
    const { data, isLoading, refetch } = useGetMoviePlayRequests({
        movieId,
    })
    return (
        data && (
            <PlayButton
                playRequests={data ?? []}
                getPlayRequests={refetch}
                loading={isLoading}
                disabled={!data || data.length === 0}
            />
        )
    )
}
