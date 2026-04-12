import { ApiHelperProps, usePageApiHelper } from '@/utils/api-crud'
import { SeriesListGetParams } from '../types/series-list.types'
import { SeriesAndEpisode } from '../types/series.types'

export interface SeriesRecentlyAiredGetParams extends SeriesListGetParams {
    days_ahead?: number
    days_behind?: number
}

interface GetProps extends ApiHelperProps<SeriesRecentlyAiredGetParams> {}

export const {
    getPage: getSeriesRecentlyAired,
    useGetPage: useGetSeriesRecentlyAired,
    queryKey: seriesRecentlyAiredQueryKey,
} = usePageApiHelper<SeriesAndEpisode, GetProps>({
    url: () => '/2/series/recently-aired',
    queryKey: (props) =>
        ['series-recently-aired', props.params].filter((f) => f !== undefined),
})
