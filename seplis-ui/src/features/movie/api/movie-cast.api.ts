import { CastMember } from '@/types/person.types'
import { ApiHelperProps, usePageApiHelper } from '@/utils/api-crud'

interface MovieCastGetParams {
    order_le?: number
    order_ge?: number
}

interface MovieTopCastGetProps extends ApiHelperProps<MovieCastGetParams> {
    movieId: number
}

export const {
    getPage: getMovieCast,
    useGetPage: useGetMovieCast,
    queryKey: getMovieCastQueryKey,
} = usePageApiHelper<CastMember, MovieTopCastGetProps>({
    url: (props) => `/2/movies/${props.movieId}/cast`,
    queryKey: (props) =>
        ['movie', props.movieId, 'cast', props.params].filter(
            (f) => f !== undefined,
        ),
})
