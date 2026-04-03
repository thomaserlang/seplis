import { queryClient } from '@/queryclient'
import {
    ApiHelperProps,
    MutationApiHelperProps,
    useApiHelper,
    useMutationApiHelper,
} from '@/utils/api-crud'
import { MovieWatchlist } from '../types/movie.types'

interface MovieWatchlistGetParams {}

interface MovieWatchlistGetProps extends ApiHelperProps<MovieWatchlistGetParams> {
    movieId: number
}

export const {
    get: getMovieWatchlist,
    useGet: useGetMovieWatchlist,
    queryKey: movieWatchlistQueryKey,
} = useApiHelper<MovieWatchlist, MovieWatchlistGetProps>({
    url: (props) => `2/movies/${props.movieId}/watchlist`,
    queryKey: (props) =>
        ['movie-Watchlist', props.movieId, props.params].filter(
            (f) => f !== undefined,
        ),
})

interface MovieWatchlistCreateProps extends MutationApiHelperProps<{}> {
    movieId: number
}

export const {
    mutation: createMovieWatchlist,
    useMutation: useCreateMovieWatchlist,
} = useMutationApiHelper<void, MovieWatchlistCreateProps>({
    url: (props) => `2/movies/${props.movieId}/watchlist`,
    method: 'PUT',
    onSuccess: ({ variables }) => {
        queryClient.setQueryData(
            movieWatchlistQueryKey({
                movieId: variables.movieId,
            }),
            {
                on_watchlist: true,
                created_at: new Date().toISOString(),
            } as MovieWatchlist,
        )
        queryClient.invalidateQueries({
            queryKey: movieWatchlistQueryKey({
                movieId: variables.movieId,
            }),
        })
    },
})

export const {
    mutation: deleteMovieWatchlist,
    useMutation: useDeleteMovieWatchlist,
} = useMutationApiHelper<void, MovieWatchlistCreateProps>({
    url: (props) => `2/movies/${props.movieId}/watchlist`,
    method: 'DELETE',
    onSuccess: ({ variables }) => {
        queryClient.setQueryData(
            movieWatchlistQueryKey({
                movieId: variables.movieId,
            }),
            {
                on_watchlist: false,
                created_at: null,
            } as MovieWatchlist,
        )
        queryClient.invalidateQueries({
            queryKey: movieWatchlistQueryKey({
                movieId: variables.movieId,
            }),
        })
    },
})
