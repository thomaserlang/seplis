import { queryClient } from '@/queryclient'
import { MutationApiHelperProps, useMutationApiHelper } from '@/utils/api-crud'
import { MovieWatched } from '../types/movie.types'
import { getMovieWatchedQueryKey } from './movie-watched.api'

interface MovieWatchedPositionUpdateProps extends MutationApiHelperProps<{
    position: number
}> {
    movieId: number
}

export const {
    mutation: updateMovieWatchedPosition,
    useMutation: useUpdateMovieWatchedPosition,
} = useMutationApiHelper<void, MovieWatchedPositionUpdateProps>({
    method: 'PUT',
    url: ({ movieId }) => `2/movies/${movieId}/watched-position`,
    onSuccess: ({ variables }) => {
        queryClient.setQueryData<MovieWatched>(
            getMovieWatchedQueryKey({ movieId: variables.movieId }),
            (oldData) =>
                oldData
                    ? {
                          ...oldData,
                          position: variables.data!.position,
                      }
                    : oldData,
        )
    },
})
