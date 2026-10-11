import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { Box, SimpleGrid, Stack, Title } from '@mantine/core'
import {
    useGetUserMovieStats,
    useGetUserSeriesStats,
} from '../api/user-stats.api'
import { WatchActivityChart } from './watch-activity-chart'
import { WatchStatsSummary } from './watch-stats-summary'

function formatWatchTime(minutes: number) {
    const hours = Math.floor(minutes / 60)
    return `${hours.toLocaleString()} ${hours === 1 ? 'hour' : 'hours'}`
}

export function UserStats({ userId }: { userId: number }) {
    const series = useGetUserSeriesStats({ userId })
    const movies = useGetUserMovieStats({ userId })

    return (
        <Stack gap="xl">
            <WatchActivityChart userId={userId} />
            <Stack gap="lg">
                <Title order={2} size="h3">
                    All time
                </Title>
                <SimpleGrid
                    cols={{ base: 1, sm: 2 }}
                    spacing="xl"
                    verticalSpacing="xl"
                >
                    <Box>
                        {series.isLoading && <PageLoader />}
                        {series.error && <ErrorBox errorObj={series.error} />}
                        {series.data && (
                            <WatchStatsSummary
                                title="Series"
                                rows={[
                                    {
                                        label: 'Episodes watched',
                                        value: series.data.episodes_watched.toLocaleString(),
                                        description: 'Includes rewatches.',
                                    },
                                    {
                                        label: 'Watch time',
                                        value: formatWatchTime(
                                            series.data
                                                .episodes_watched_minutes,
                                        ),
                                        description:
                                            'Total episode runtime, including rewatches.',
                                    },
                                    {
                                        label: 'Series watched',
                                        value: series.data.series_watched.toLocaleString(),
                                    },
                                    {
                                        label: 'Series finished',
                                        value: series.data.series_finished.toLocaleString(),
                                    },
                                    {
                                        label: 'Series on watchlist',
                                        value: series.data.series_watchlist.toLocaleString(),
                                    },
                                ]}
                            />
                        )}
                    </Box>
                    <Box>
                        {movies.isLoading && <PageLoader />}
                        {movies.error && <ErrorBox errorObj={movies.error} />}
                        {movies.data && (
                            <WatchStatsSummary
                                title="Movies"
                                rows={[
                                    {
                                        label: 'Movies watched',
                                        value: movies.data.movies_watched.toLocaleString(),
                                        description: 'Each movie counted once.',
                                    },
                                    {
                                        label: 'Watch time',
                                        value: formatWatchTime(
                                            movies.data.total_watch_minutes,
                                        ),
                                        description:
                                            'Total movie runtime, including rewatches.',
                                    },
                                    {
                                        label: 'Movie rewatches',
                                        value: Math.max(
                                            0,
                                            movies.data.movie_watch_count -
                                                movies.data.movies_watched,
                                        ).toLocaleString(),
                                    },
                                    {
                                        label: 'Movies on watchlist',
                                        value: movies.data.movies_watchlist.toLocaleString(),
                                    },
                                ]}
                            />
                        )}
                    </Box>
                </SimpleGrid>
            </Stack>
        </Stack>
    )
}
