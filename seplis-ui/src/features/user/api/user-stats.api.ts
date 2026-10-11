import { ApiHelperProps, useApiHelper } from '@/utils/api-crud'
import {
    UserMovieStats,
    UserSeriesStats,
    UserWatchActivityPeriod,
} from '../types/user-stats.types'

interface Props extends ApiHelperProps {
    userId: number
}

export const {
    useGet: useGetUserSeriesStats,
    queryKey: userSeriesStatsQueryKey,
} = useApiHelper<UserSeriesStats, Props>({
    url: () => '2/series/user-stats',
    queryKey: ({ userId }) => ['user', 'series-stats', userId],
})

export const { useGet: useGetUserMovieStats } = useApiHelper<
    UserMovieStats,
    Props
>({
    url: () => '2/movies/user-stats',
    queryKey: ({ userId }) => ['user', 'movie-stats', userId],
})

interface ActivityProps extends ApiHelperProps<{
    year: number
    month?: number
}> {
    userId: number
}

export const { useGet: useGetUserWatchActivity } = useApiHelper<
    UserWatchActivityPeriod[],
    ActivityProps
>({
    url: () => '2/users/me/watch-activity',
    queryKey: ({ userId, params }) => [
        'user',
        'watch-activity',
        userId,
        params,
    ],
})
