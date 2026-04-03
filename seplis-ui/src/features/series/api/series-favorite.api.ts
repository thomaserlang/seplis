import { queryClient } from '@/queryclient'
import {
    ApiHelperProps,
    MutationApiHelperProps,
    useApiHelper,
    useMutationApiHelper,
} from '@/utils/api-crud'
import { SeriesFavorite } from '../types/series.types'

interface SeriesFavoriteGetParams {}

interface SeriesFavoriteGetProps extends ApiHelperProps<SeriesFavoriteGetParams> {
    seriesId: number
}

export const {
    get: getSeriesFavorite,
    useGet: useGetSeriesFavorite,
    queryKey: seriesFavoriteQueryKey,
} = useApiHelper<SeriesFavorite, SeriesFavoriteGetProps>({
    url: (props) => `2/series/${props.seriesId}/favorite`,
    queryKey: (props) =>
        ['series-favorite', props.seriesId, props.params].filter(
            (f) => f !== undefined,
        ),
})

interface SeriesFavoriteCreateProps extends MutationApiHelperProps<{}> {
    seriesId: number
}

export const {
    mutation: createSeriesFavorite,
    useMutation: useCreateSeriesFavorite,
} = useMutationApiHelper<void, SeriesFavoriteCreateProps>({
    url: (props) => `2/series/${props.seriesId}/favorite`,
    method: 'PUT',
    onSuccess: ({ variables }) => {
        queryClient.setQueryData(
            seriesFavoriteQueryKey({
                seriesId: variables.seriesId,
            }),
            {
                favorite: true,
                created_at: new Date().toISOString(),
            } as SeriesFavorite,
        )
        queryClient.invalidateQueries({
            queryKey: seriesFavoriteQueryKey({
                seriesId: variables.seriesId,
            }),
        })
    },
})

export const {
    mutation: deleteSeriesFavorite,
    useMutation: useDeleteSeriesFavorite,
} = useMutationApiHelper<void, SeriesFavoriteCreateProps>({
    url: (props) => `2/series/${props.seriesId}/favorite`,
    method: 'DELETE',
    onSuccess: ({ variables }) => {
        queryClient.setQueryData(
            seriesFavoriteQueryKey({
                seriesId: variables.seriesId,
            }),
            {
                favorite: false,
                created_at: null,
            } as SeriesFavorite,
        )
        queryClient.invalidateQueries({
            queryKey: seriesFavoriteQueryKey({
                seriesId: variables.seriesId,
            }),
        })
    },
})
