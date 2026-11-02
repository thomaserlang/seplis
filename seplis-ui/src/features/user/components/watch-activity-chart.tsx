import { ErrorBox } from '@/components/error-box'
import { PageLoader } from '@/components/page-loader'
import { BarChart } from '@mantine/charts'
import '@mantine/charts/styles.css'
import {
    ActionIcon,
    Box,
    Divider,
    Group,
    Paper,
    SegmentedControl,
    Stack,
    Text,
    Title,
    Tooltip,
} from '@mantine/core'
import { CaretLeftIcon, CaretRightIcon } from '@phosphor-icons/react'
import { useState } from 'react'
import { useGetUserWatchActivity } from '../api/user-stats.api'

function hours(minutes: number) {
    const value = Math.floor(minutes / 60)
    return `${value.toLocaleString()} ${value === 1 ? 'hour' : 'hours'}`
}

const controlStyles = {
    root: { background: 'var(--card)' },
    indicator: { background: 'var(--secondary)' },
}

export function WatchActivityChart({ userId }: { userId: number }) {
    const now = new Date()
    const [view, setView] = useState('day')
    const [media, setMedia] = useState('all')
    const [date, setDate] = useState(
        () => new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1)),
    )
    const year = date.getUTCFullYear()
    const month = date.getUTCMonth()
    const isDay = view === 'day'
    const isYear = view === 'year'
    const currentYear = year === now.getUTCFullYear()
    const currentPeriod =
        isYear || (currentYear && (!isDay || month === now.getUTCMonth()))
    const { data, isLoading, error } = useGetUserWatchActivity({
        userId,
        params: {
            year: isYear ? undefined : year,
            month: isDay ? month + 1 : undefined,
        },
    })
    const periodLabel = isYear
        ? 'All years'
        : date.toLocaleDateString(undefined, {
              year: 'numeric',
              ...(isDay ? { month: 'long' as const } : {}),
              timeZone: 'UTC',
          })
    const records = (data ?? [])
        .filter((item) => item.date <= now.toISOString().slice(0, 10))
        .map((item) => {
            const day = new Date(`${item.date}T00:00:00Z`)
            const partial =
                day.getUTCFullYear() === now.getUTCFullYear() &&
                (isYear || day.getUTCMonth() === now.getUTCMonth()) &&
                (!isDay || day.getUTCDate() === now.getUTCDate())
            const minutes =
                media === 'series'
                    ? item.series_minutes
                    : media === 'movies'
                      ? item.movie_minutes
                      : item.series_minutes + item.movie_minutes
            return {
                ...item,
                label: isYear
                    ? String(day.getUTCFullYear())
                    : isDay
                      ? String(day.getUTCDate())
                      : day.toLocaleDateString(undefined, {
                            month: 'short',
                            timeZone: 'UTC',
                        }),
                fullLabel: day.toLocaleDateString(undefined, {
                    year: 'numeric',
                    ...(!isYear ? { month: 'long' as const } : {}),
                    ...(isDay ? { day: 'numeric' as const } : {}),
                    timeZone: 'UTC',
                }),
                partial,
                color: partial
                    ? 'var(--muted-foreground)'
                    : 'var(--foreground)',
                minutes,
                hours: minutes / 60,
            }
        })
    const total = records.reduce((sum, item) => sum + item.minutes, 0)
    const navigate = (direction: number) =>
        setDate(
            new Date(
                Date.UTC(
                    year + (isDay ? 0 : direction),
                    month + (isDay ? direction : 0),
                    1,
                ),
            ),
        )

    return (
        <Stack gap="md">
            <Group justify="space-between">
                <Title order={2} size="h3">
                    Watch time
                </Title>
                <SegmentedControl
                    aria-label="Media type"
                    value={media}
                    onChange={setMedia}
                    styles={controlStyles}
                    data={[
                        { label: 'All', value: 'all' },
                        { label: 'Series', value: 'series' },
                        { label: 'Movies', value: 'movies' },
                    ]}
                />
            </Group>
            <Divider />
            <Group justify="space-between">
                <Group gap="xs" wrap="nowrap">
                    {!isYear && (
                        <Tooltip
                            label={isDay ? 'Previous month' : 'Previous year'}
                        >
                            <ActionIcon
                                variant="default"
                                aria-label={
                                    isDay ? 'Previous month' : 'Previous year'
                                }
                                onClick={() => navigate(-1)}
                                disabled={year <= 1}
                            >
                                <CaretLeftIcon />
                            </ActionIcon>
                        </Tooltip>
                    )}
                    <Text fw={600} ta="center" w={150}>
                        {periodLabel}
                    </Text>
                    {!isYear && (
                        <Tooltip label={isDay ? 'Next month' : 'Next year'}>
                            <ActionIcon
                                variant="default"
                                aria-label={isDay ? 'Next month' : 'Next year'}
                                onClick={() => navigate(1)}
                                disabled={currentPeriod}
                            >
                                <CaretRightIcon />
                            </ActionIcon>
                        </Tooltip>
                    )}
                </Group>
                <SegmentedControl
                    aria-label="Chart period"
                    value={view}
                    onChange={(value) => {
                        setView(value)
                        if (
                            value === 'day' &&
                            currentYear &&
                            month > now.getUTCMonth()
                        ) {
                            setDate(
                                new Date(Date.UTC(year, now.getUTCMonth(), 1)),
                            )
                        }
                    }}
                    styles={controlStyles}
                    data={[
                        { label: 'Day', value: 'day' },
                        { label: 'Month', value: 'month' },
                        { label: 'Year', value: 'year' },
                    ]}
                />
            </Group>
            {isLoading && (
                <Box mih={300}>
                    <PageLoader />
                </Box>
            )}
            {error && <ErrorBox errorObj={error} />}
            {data && !error && (
                <>
                    <Group gap="xs" align="baseline">
                        <Text size="xl" fw={600}>
                            {hours(total)}
                        </Text>
                        <Text c="dimmed">
                            {currentPeriod ? 'so far' : 'total'}
                        </Text>
                    </Group>
                    <BarChart
                        h={260}
                        data={records}
                        dataKey="label"
                        series={[
                            {
                                name: 'hours',
                                label: 'Watch time',
                                color: 'var(--foreground)',
                            },
                        ]}
                        maxBarWidth={36}
                        gridColor="var(--border)"
                        textColor="var(--muted-foreground)"
                        cursorFill="var(--secondary)"
                        yAxisProps={{ width: 85, allowDecimals: false }}
                        xAxisProps={{ minTickGap: 12 }}
                        valueFormatter={(value) => hours(value * 60)}
                        barProps={{ isAnimationActive: false }}
                        tooltipProps={{
                            content: ({ label, active }) => {
                                const record = records.find(
                                    (item) => item.label === String(label),
                                )
                                if (!active || !record) return null
                                return (
                                    <Paper
                                        p="sm"
                                        withBorder
                                        bg="var(--popover)"
                                    >
                                        <Text fw={600} mb="xs">
                                            {record.fullLabel}
                                            {record.partial ? ' (so far)' : ''}
                                        </Text>
                                        <Group justify="space-between" gap="lg">
                                            <Text>Total</Text>
                                            <Text fw={600}>
                                                {hours(record.minutes)}
                                            </Text>
                                        </Group>
                                        {media === 'all' && (
                                            <>
                                                <Group
                                                    justify="space-between"
                                                    gap="lg"
                                                >
                                                    <Text c="dimmed">
                                                        Series
                                                    </Text>
                                                    <Text>
                                                        {hours(
                                                            record.series_minutes,
                                                        )}
                                                    </Text>
                                                </Group>
                                                <Group
                                                    justify="space-between"
                                                    gap="lg"
                                                >
                                                    <Text c="dimmed">
                                                        Movies
                                                    </Text>
                                                    <Text>
                                                        {hours(
                                                            record.movie_minutes,
                                                        )}
                                                    </Text>
                                                </Group>
                                            </>
                                        )}
                                    </Paper>
                                )
                            },
                        }}
                    />
                    {total === 0 && (
                        <Text c="dimmed">
                            No watch activity in this period.
                        </Text>
                    )}
                </>
            )}
        </Stack>
    )
}
