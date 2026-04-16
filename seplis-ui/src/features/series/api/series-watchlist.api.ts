import { queryClient } from '@/queryclient'
import {
    ApiHelperProps,
    MutationApiHelperProps,
    useApiHelper,
    useMutationApiHelper,
} from '@/utils/api-crud'
import { SeriesWatchlist } from '../types/series.types'

interface SeriesWatchlistGetParams {}

interface SeriesWatchlistGetProps extends ApiHelperProps<SeriesWatchlistGetParams> {
    seriesId: number
}

export const {
    get: getSeriesWatchlist,
    useGet: useGetSeriesWatchlist,
    queryKey: seriesWatchlistQueryKey,
} = useApiHelper<SeriesWatchlist, SeriesWatchlistGetProps>({
    url: (props) => `2/series/${props.seriesId}/watchlist`,
    queryKey: (props) =>
        ['series', props.seriesId, 'watchlist', props.params].filter(
            (f) => f !== undefined,
        ),
})

interface SeriesWatchlistCreateProps extends MutationApiHelperProps<{}> {
    seriesId: number
}

export const {
    mutation: createSeriesWatchlist,
    useMutation: useCreateSeriesWatchlist,
} = useMutationApiHelper<void, SeriesWatchlistCreateProps>({
    url: (props) => `2/series/${props.seriesId}/watchlist`,
    method: 'PUT',
    onSuccess: ({ variables }) => {
        queryClient.setQueryData(
            seriesWatchlistQueryKey({
                seriesId: variables.seriesId,
            }),
            {
                on_watchlist: true,
                created_at: new Date().toISOString(),
            } as SeriesWatchlist,
        )
        queryClient.invalidateQueries({
            queryKey: seriesWatchlistQueryKey({
                seriesId: variables.seriesId,
            }),
        })
    },
})

export const {
    mutation: deleteSeriesWatchlist,
    useMutation: useDeleteSeriesWatchlist,
} = useMutationApiHelper<void, SeriesWatchlistCreateProps>({
    url: (props) => `2/series/${props.seriesId}/watchlist`,
    method: 'DELETE',
    onSuccess: ({ variables }) => {
        queryClient.setQueryData(
            seriesWatchlistQueryKey({
                seriesId: variables.seriesId,
            }),
            {
                on_watchlist: false,
                created_at: null,
            } as SeriesWatchlist,
        )
        queryClient.invalidateQueries({
            queryKey: seriesWatchlistQueryKey({
                seriesId: variables.seriesId,
            }),
        })
    },
})
