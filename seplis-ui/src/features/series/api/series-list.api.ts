import { ApiHelperProps, usePageApiHelper } from '@/utils/api-crud'
import { SeriesListGetParams } from '../types/series-list.types'
import { Series } from '../types/series.types'

interface GetProps extends ApiHelperProps<SeriesListGetParams> {}

export const {
    getPage: getSeriesList,
    useGetPage: useGetSeriesList,
    queryKey: seriesListQueryKey,
} = usePageApiHelper<Series, GetProps>({
    url: () => '/2/series',
    queryKey: (props) =>
        ['series-list', props.params].filter((f) => f !== undefined),
    formatParams: (props) => ({
        per_page: 100,
        ...props.params,
    }),
})
