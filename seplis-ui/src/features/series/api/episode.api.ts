import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import { Episode } from '../types/episodes.types'

interface EpisodeParams {
    expand?: string[]
}

interface EpisodeProps extends ApiHelperProps<EpisodeParams> {
    seriesId: number
    number: number
}

export const {
    get: getEpisode,
    useGet: useGetEpisode,
    queryKey: episodeQueryKey,
} = useApiHelper<Episode, EpisodeProps>({
    url: (props) => `2/series/${props.seriesId}/episodes/${props.number}`,
    queryKey: (props) =>
        ['episode', props.seriesId, props.number, props.params].filter(
            (f) => f !== undefined,
        ),
})
