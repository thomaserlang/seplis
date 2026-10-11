import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import { SeriesUserStats } from '../types/series.types'

interface Props extends ApiHelperProps {
    seriesId: number
}

export const {
    useGet: useGetSeriesUserStats,
    queryKey: seriesUserStatsQueryKey,
} = useApiHelper<SeriesUserStats, Props>({
    url: ({ seriesId }) => `2/series/${seriesId}/user-stats`,
    queryKey: ({ seriesId }) => ['series', seriesId, 'user-stats'],
})
