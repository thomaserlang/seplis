import { getUserWatchedQueryKey } from '@/features/user'
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
        invalidateMovieWatched({
            movieId: variables.movieId,
            data,
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
        invalidateMovieWatched({
            movieId: variables.movieId,
            data,
        })
    },
})

export function invalidateMovieWatched({
    movieId,
    data,
}: {
    movieId: number
    data?: MovieWatched
}) {
    if (data) {
        queryClient.setQueryData(movieWatchedQueryKey({ movieId }), data)
    } else {
        queryClient.invalidateQueries({
            queryKey: movieWatchedQueryKey({ movieId }),
        })
    }
    queryClient.invalidateQueries({
        queryKey: movieWatchlistQueryKey({ movieId }),
    })
    queryClient.invalidateQueries({
        queryKey: getUserWatchedQueryKey({}),
    })
}
