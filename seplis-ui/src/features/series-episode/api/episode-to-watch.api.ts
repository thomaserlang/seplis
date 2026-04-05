import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import { Episode } from '../types/episode.types'

interface EpisodeToWatchProps extends ApiHelperProps<{}> {
    seriesId: number
}

export const {
    get: getEpisodeToWatch,
    useGet: useGetEpisodeToWatch,
    queryKey: episodeToWatchQueryKey,
} = useApiHelper<Episode | null, EpisodeToWatchProps>({
    url: ({ seriesId }) => `2/series/${seriesId}/episode-to-watch`,
    queryKey: ({ seriesId }) => ['episode-to-watch', seriesId],
})
