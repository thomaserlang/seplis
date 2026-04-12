import { ApiHelperProps, usePageApiHelper } from '@/utils/api-crud'
import { Movie } from '../types/movie.types'
import { MoviesGetParams } from '../types/movies.types'

export interface GetProps extends ApiHelperProps<MoviesGetParams> {}

export const {
    getPage: getMovies,
    useGetPage: useGetMovies,
    queryKey: moviesQueryKey,
} = usePageApiHelper<Movie, GetProps>({
    url: () => '/2/movies',
    queryKey: (props) =>
        ['movies', props.params].filter((f) => f !== undefined),
})
