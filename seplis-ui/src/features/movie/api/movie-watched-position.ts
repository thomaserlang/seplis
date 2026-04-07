import { MutationApiHelperProps, useMutationApiHelper } from '@/utils/api-crud'

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
})
