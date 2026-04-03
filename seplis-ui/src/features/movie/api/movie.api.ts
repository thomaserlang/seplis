import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import { Movie } from '../types/movie.types'

interface Params {}

interface MovieProps extends ApiHelperProps<Params> {
    movieId: number
}

export const {
    get: getMovie,
    useGet: useGetMovie,
    queryKey: movieQueryKey,
} = useApiHelper<Movie, MovieProps>({
    url: (props) => `2/movies/${props.movieId}`,
    queryKey: (props) =>
        ['movie', props.movieId, props.params].filter((f) => f !== undefined),
})
