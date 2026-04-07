import { MutationApiHelperProps, useMutationApiHelper } from '@/utils/api-crud'

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
})
