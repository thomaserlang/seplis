import {
    ApiHelperProps,
    MutationApiHelperProps,
    useApiHelper,
    useMutationApiHelper,
} from '@/utils/api-crud'
import {
    SeriesUserSettings,
    SeriesUserSettingsUpdate,
} from '../types/series.types'

interface SeriesUserSettingsGetProps extends ApiHelperProps<{}> {
    seriesId: number
}

export const {
    get: getSeriesUserSettings,
    useGet: useGetSeriesUserSettings,
    queryKey: seriesUserSettingsQueryKey,
} = useApiHelper<SeriesUserSettings, SeriesUserSettingsGetProps>({
    url: ({ seriesId }) => `2/series/${seriesId}/user-settings`,
    queryKey: ({ seriesId }) => ['series', seriesId, 'user-settings'],
})

interface SeriesUserSettingsUpdateProps extends MutationApiHelperProps<SeriesUserSettingsUpdate> {
    seriesId: number
}

export const {
    mutation: updateSeriesUserSettings,
    useMutation: useUpdateSeriesUserSettings,
} = useMutationApiHelper<void, SeriesUserSettingsUpdateProps>({
    method: 'PUT',
    url: ({ seriesId }) => `2/series/${seriesId}/user-settings`,
})
