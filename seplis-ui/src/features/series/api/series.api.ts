import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import { Series } from '../types/series.types'

interface Params {}

interface SeriesProps extends ApiHelperProps<Params> {
    seriesId: number
}

export const {
    get: getSeries,
    useGet: useGetSeries,
    queryKey: seriesQueryKey,
} = useApiHelper<Series, SeriesProps>({
    url: (props) => `2/series/${props.seriesId}`,
    queryKey: (props) =>
        ['series', props.seriesId, props.params].filter((f) => f !== undefined),
})
