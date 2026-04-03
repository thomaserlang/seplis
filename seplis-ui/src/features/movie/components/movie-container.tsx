import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { useGetMovie } from '../api/movie.api'
import { MovieView } from './movie-view'

interface Props {
    movieId: number
}

export function MovieContainer({ movieId }: Props) {
    const { data, isLoading, error } = useGetMovie({
        movieId,
    })

    return (
        <>
            {isLoading && <PageLoader />}
            {error && !data && <ErrorBox errorObj={error} />}
            {data && <MovieView movie={data} />}
        </>
    )
}
