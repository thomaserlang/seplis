import { queryClient } from '@/queryclient'
import { MutationApiHelperProps, useMutationApiHelper } from '@/utils/api-crud'
import { EpisodeWatched } from '../types/episode.types'
import { episodeLastWatchedQueryKey } from './episode-last-watched.api'
import { episodeToWatchQueryKey } from './episode-to-watch.api'
import { getEpisodeWatchedQueryKey } from './episode-watched.api'

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
        queryClient.setQueryData<EpisodeWatched>(
            getEpisodeWatchedQueryKey({
                seriesId: variables.seriesId,
                episodeNumber: variables.episodeNumber,
            }),
            (oldData) =>
                oldData
                    ? {
                          ...oldData,
                          position: variables.data!.position,
                      }
                    : oldData,
        )
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
