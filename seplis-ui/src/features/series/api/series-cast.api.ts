import { CastMember } from '@/types/person.types'
import { ApiHelperProps, usePageApiHelper } from '@/utils/api-crud'

interface SeriesCastGetParams {
    order_le?: number
    order_ge?: number
}

interface SeriesCastGetProps extends ApiHelperProps<SeriesCastGetParams> {
    seriesId: number
}

export const {
    getPage: getSeriesCast,
    useGetPage: useGetSeriesCast,
    queryKey: getSeriesCastQueryKey,
} = usePageApiHelper<CastMember, SeriesCastGetProps>({
    url: (props) => `/2/series/${props.seriesId}/cast`,
    queryKey: (props) =>
        ['series', props.seriesId, 'cast', props.params].filter(
            (f) => f !== undefined,
        ),
})
