import { queryClient } from '@/queryclient'
import { MutationApiHelperProps, useMutationApiHelper } from '@/utils/api-crud'
import { episodeLastWatchedQueryKey } from './episode-last-watched.api'
import { episodeToWatchQueryKey } from './episode-to-watch.api'
import { episodeWatchedQueryKey } from './episode-watched.api'

interface EpisodeWatchedPositionUpdateProps extends MutationApiHelperProps<{
    position: number
}> {
    seriesId: number
    episodeNumber: number
}

export const {
    mutation: updateEpisodeWatchedPosition,
    useMutation: useUpdateEpisodeWatchedPosition,
} = useMutationApiHelper<void, EpisodeWatchedPositionUpdateProps>({
    method: 'PUT',
    url: ({ seriesId, episodeNumber }) =>
        `2/series/${seriesId}/episodes/${episodeNumber}/watched-position`,
    onSuccess: ({ variables }) => {
        queryClient.invalidateQueries({
            queryKey: episodeWatchedQueryKey({
                seriesId: variables.seriesId,
                episodeNumber: variables.episodeNumber,
            }),
        })
        queryClient.invalidateQueries({
            queryKey: episodeLastWatchedQueryKey({
                seriesId: variables.seriesId,
            }),
        })
        queryClient.invalidateQueries({
            queryKey: episodeToWatchQueryKey({ seriesId: variables.seriesId }),
        })
    },
})
