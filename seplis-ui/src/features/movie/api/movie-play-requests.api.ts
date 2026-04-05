import { PlayRequest } from '@/features/play'
import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'

interface MoviePlayRequestsGetProps extends ApiHelperProps<{}> {
    movieId: number
}

export const {
    get: getMoviePlayRequests,
    useGet: useGetMoviePlayRequests,
    queryKey: moviePlayRequestsQueryKey,
} = useApiHelper<PlayRequest[], MoviePlayRequestsGetProps>({
    url: ({ movieId }) => `2/movies/${movieId}/play-servers`,
    queryKey: ({ movieId }) => ['movie-play-requests', movieId],
})
