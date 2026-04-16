import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import { Episode } from '../types/episode.types'

interface EpisodeLastWatchedGetProps extends ApiHelperProps<{}> {
    seriesId: number
}

export const {
    get: getEpisodeLastWatched,
    useGet: useGetEpisodeLastWatched,
    queryKey: episodeLastWatchedQueryKey,
} = useApiHelper<Episode | null, EpisodeLastWatchedGetProps>({
    url: ({ seriesId }) => `2/series/${seriesId}/episode-last-watched`,
    queryKey: ({ seriesId }) => ['series', seriesId, 'episode-last-watched'],
})
