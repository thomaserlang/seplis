import { PlayRequest } from '@/features/play'
import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'

interface EpisodePlayRequestsGetProps extends ApiHelperProps<{}> {
    seriesId: number
    episodeNumber: number
}

export const {
    get: getEpisodePlayRequests,
    useGet: useGetEpisodePlayRequests,
    queryKey: episodePlayRequestsQueryKey,
} = useApiHelper<PlayRequest[], EpisodePlayRequestsGetProps>({
    url: ({ seriesId, episodeNumber }) =>
        `2/series/${seriesId}/episodes/${episodeNumber}/play-servers`,
    queryKey: ({ seriesId, episodeNumber }) => [
        'episode-play-requests',
        seriesId,
        episodeNumber,
    ],
})
