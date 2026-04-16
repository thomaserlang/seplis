import { queryClient } from '@/queryclient'
import { MutationApiHelperProps, useMutationApiHelper } from '@/utils/api-crud'

interface EpisodeRangeWatchedProps extends MutationApiHelperProps<
    {
        from_episode_number: number
        to_episode_number: number
    },
    {}
> {
    seriesId: number
}

export const {
    mutation: setEpisodeRangeWatched,
    useMutation: useSetEpisodeRangeWatched,
} = useMutationApiHelper<{}, EpisodeRangeWatchedProps>({
    method: 'POST',
    url: ({ seriesId }) => `2/series/${seriesId}/episodes/watched-range`,
    onSuccess: ({ variables }) => {
        queryClient.invalidateQueries({
            queryKey: ['series', variables.seriesId],
        })
    },
})
