import { queryClient } from '@/queryclient'
import {
    ApiHelperProps,
    MutationApiHelperProps,
    useApiHelper,
    useMutationApiHelper,
} from '@/utils/api-crud'
import { MovieWatched } from '../types/movie.types'
import { movieWatchlistQueryKey } from './movie-watchlist.api'

interface MovieWatchedGetProps extends ApiHelperProps<{}> {
    movieId: number
}

export const {
    get: getMovieWatched,
    useGet: useGetMovieWatched,
    queryKey: movieWatchedQueryKey,
} = useApiHelper<MovieWatched, MovieWatchedGetProps>({
    url: ({ movieId }) => `2/movies/${movieId}/watched`,
    queryKey: ({ movieId }) => ['movie-watched', movieId],
})

interface MovieWatchedIncrementProps extends MutationApiHelperProps<{}> {
    movieId: number
}

export const {
    mutation: incrementMovieWatched,
    useMutation: useIncrementMovieWatched,
} = useMutationApiHelper<MovieWatched, MovieWatchedIncrementProps>({
    method: 'POST',
    url: ({ movieId }) => `2/movies/${movieId}/watched`,
    onSuccess: ({ data, variables }) => {
        queryClient.setQueryData(
            movieWatchedQueryKey({ movieId: variables.movieId }),
            data,
        )
        queryClient.invalidateQueries({
            queryKey: movieWatchlistQueryKey({ movieId: variables.movieId }),
        })
    },
})

interface MovieWatchedDecrementProps extends MutationApiHelperProps<{}> {
    movieId: number
}

export const {
    mutation: decrementMovieWatched,
    useMutation: useDecrementMovieWatched,
} = useMutationApiHelper<MovieWatched, MovieWatchedDecrementProps>({
    method: 'DELETE',
    url: ({ movieId }) => `2/movies/${movieId}/watched`,
    onSuccess: ({ data, variables }) => {
        queryClient.setQueryData(
            movieWatchedQueryKey({ movieId: variables.movieId }),
            data,
        )
        queryClient.invalidateQueries({
            queryKey: movieWatchlistQueryKey({ movieId: variables.movieId }),
        })
    },
})
