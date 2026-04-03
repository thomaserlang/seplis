import { queryClient } from '@/queryclient'
import {
    ApiHelperProps,
    MutationApiHelperProps,
    useApiHelper,
    useMutationApiHelper,
} from '@/utils/api-crud'
import { MovieFavorite } from '../types/movie.types'

interface MovieFavoriteGetParams {}

interface MovieFavoriteGetProps extends ApiHelperProps<MovieFavoriteGetParams> {
    movieId: number
}

export const {
    get: getMovieFavorite,
    useGet: useGetMovieFavorite,
    queryKey: movieFavoriteQueryKey,
} = useApiHelper<MovieFavorite, MovieFavoriteGetProps>({
    url: (props) => `2/movies/${props.movieId}/favorite`,
    queryKey: (props) =>
        ['movie-favorite', props.movieId, props.params].filter(
            (f) => f !== undefined,
        ),
})

interface MovieFavoriteCreateProps extends MutationApiHelperProps<{}> {
    movieId: number
}

export const {
    mutation: createMovieFavorite,
    useMutation: useCreateMovieFavorite,
} = useMutationApiHelper<void, MovieFavoriteCreateProps>({
    url: (props) => `2/movies/${props.movieId}/favorite`,
    method: 'PUT',
    onSuccess: ({ variables }) => {
        queryClient.setQueryData(
            movieFavoriteQueryKey({
                movieId: variables.movieId,
            }),
            {
                favorite: true,
                created_at: new Date().toISOString(),
            } as MovieFavorite,
        )
        queryClient.invalidateQueries({
            queryKey: movieFavoriteQueryKey({
                movieId: variables.movieId,
            }),
        })
    },
})

export const {
    mutation: deleteMovieFavorite,
    useMutation: useDeleteMovieFavorite,
} = useMutationApiHelper<void, MovieFavoriteCreateProps>({
    url: (props) => `2/movies/${props.movieId}/favorite`,
    method: 'DELETE',
    onSuccess: ({ variables }) => {
        queryClient.setQueryData(
            movieFavoriteQueryKey({
                movieId: variables.movieId,
            }),
            {
                favorite: false,
                created_at: null,
            } as MovieFavorite,
        )
        queryClient.invalidateQueries({
            queryKey: movieFavoriteQueryKey({
                movieId: variables.movieId,
            }),
        })
    },
})
