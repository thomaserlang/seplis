import { ApiHelperProps, usePageApiHelper } from '@/utils/api-crud'
import { SeriesListGetParams } from '../types/series-list.types'
import { SeriesAndEpisode } from '../types/series.types'

interface GetProps extends ApiHelperProps<SeriesListGetParams> {}

export const {
    getPage: getSeriesToWatch,
    useGetPage: useGetSeriesToWatch,
    queryKey: getSeriesToWatchQueryKey,
} = usePageApiHelper<SeriesAndEpisode, GetProps>({
    url: () => '/2/series/to-watch',
    queryKey: () => ['series-to-watch'],
})
