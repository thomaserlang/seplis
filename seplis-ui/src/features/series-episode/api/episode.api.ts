import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import { Episode } from '../types/episode.types'

interface EpisodeParams {
    expand?: string[]
}

interface EpisodeProps extends ApiHelperProps<EpisodeParams> {
    seriesId: number
    episodeNumber: number
}

export const {
    get: getEpisode,
    useGet: useGetEpisode,
    queryKey: episodeQueryKey,
} = useApiHelper<Episode, EpisodeProps>({
    url: (props) =>
        `2/series/${props.seriesId}/episodes/${props.episodeNumber}`,
    queryKey: (props) =>
        [
            'series',
            props.seriesId,
            'episode',
            props.episodeNumber,
            props.params,
        ].filter((f) => f !== undefined),
})
