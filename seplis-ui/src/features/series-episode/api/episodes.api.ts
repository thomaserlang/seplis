import { ApiHelperProps, usePageApiHelper } from '@/utils/api-crud'
import { Episode } from '../types/episode.types'

interface EpisodesParams {
    season?: number
    episode?: number
    number?: number
    air_date?: string
    air_date_ge?: string
    air_date_le?: string
    expand?: string[]
}

interface EpisodesProps extends ApiHelperProps<EpisodesParams> {
    seriesId: number
}

export const {
    getPage: getEpisodes,
    useGetPage: useGetEpisodes,
    queryKey: episodesQueryKey,
} = usePageApiHelper<Episode, EpisodesProps>({
    url: (props) => `2/series/${props.seriesId}/episodes`,
    queryKey: (props) =>
        ['episodes', props.seriesId, props.params].filter(
            (f) => f !== undefined,
        ),
})
