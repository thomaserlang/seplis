import { MediaInfo, MediaMetaItem, MediaStatus } from '@/components/media-info'
import { mediaTypes } from '@/features/media-type'
import {
    EpisodeLastWatchedCard,
    EpisodeToWatchCard,
} from '@/features/series-episode'
import { useActiveUser } from '@/features/user'
import { langCodeToLang } from '@/utils/language.utils'
import { Box, Flex } from '@mantine/core'
import { useGetSeriesUserStats } from '../api/series-user-stats.api'
import { Series, SeriesUserStats } from '../types/series.types'
import { SeriesFavoriteButton } from './series-favorite-button'
import { SeriesWatchlistButton } from './series-watchlist-button'

interface Props {
    series: Series
    children?: React.ReactNode
}

const STATUS: Record<number, MediaStatus> = {
    0: { label: 'Unknown', dot: 'oklch(0.6 0 0)' },
    1: { label: 'Returning', dot: 'oklch(0.7 0.17 175)' },
    2: { label: 'Ended', dot: 'oklch(0.6 0.2 25)' },
    3: { label: 'Cancelled', dot: 'oklch(0.7 0.18 55)' },
    4: { label: 'In production', dot: 'oklch(0.6 0.2 250)' },
    5: { label: 'Planned', dot: 'oklch(0.55 0.22 295)' },
}

export function SeriesInfo({ series, children }: Props) {
    const [user] = useActiveUser()
    const { data: stats } = useGetSeriesUserStats({
        seriesId: series.id,
        options: { enabled: !!user },
    })

    return (
        <MediaInfo
            posterUrl={
                series.poster_image
                    ? `${series.poster_image.url}@SX320.webp`
                    : undefined
            }
            accentHue={mediaTypes['series'].accentHue}
            status={series.status != null ? STATUS[series.status] : undefined}
            title={series.title || series.original_title || 'Unknown title'}
            originalTitle={series.original_title}
            tagline={series.tagline}
            metaItems={SeriesMetaItems({
                series,
                showYearRange: true,
                showRuntime: true,
                showLanguage: true,
                showRating: true,
                showSeasons: true,
                showTotalEpisodes: true,
                stats: user ? stats : undefined,
            })}
            genres={series.genres}
            plot={series.plot}
        >
            <Flex gap="1rem" direction="column">
                <Flex gap="0.5rem" wrap="wrap">
                    <SeriesWatchlistButton seriesId={series.id} />
                    <SeriesFavoriteButton seriesId={series.id} />
                </Flex>

                <Flex gap="1rem" wrap="wrap">
                    <Box style={{ flex: '1 1 18rem' }} miw="0">
                        <EpisodeToWatchCard seriesId={series.id} />
                    </Box>
                    <Box style={{ flex: '1 1 18rem' }} miw="0">
                        <EpisodeLastWatchedCard seriesId={series.id} />
                    </Box>
                </Flex>

                {children}
            </Flex>
        </MediaInfo>
    )
}

export function SeriesMetaItems({
    series,
    showYearRange,
    showRuntime,
    showLanguage,
    showRating,
    showSeasons,
    showTotalEpisodes,
    stats,
}: {
    series: Series
    showYearRange?: boolean
    showRuntime?: boolean
    showLanguage?: boolean
    showRating?: boolean
    showSeasons?: boolean
    showTotalEpisodes?: boolean
    stats?: SeriesUserStats
}) {
    const startYear = series.premiered?.substring(0, 4)
    const endYear = series.ended?.substring(0, 4)
    const yearRange = startYear
        ? endYear && endYear !== startYear
            ? `${startYear}–${endYear}`
            : startYear
        : null

    const items = [
        showYearRange && yearRange ? { label: 'Year', value: yearRange } : null,
        showRuntime && series.runtime
            ? { label: 'Runtime', value: `${series.runtime} min` }
            : null,
        showLanguage && series.language
            ? { label: 'Language', value: langCodeToLang(series.language) }
            : null,
        showRating && series.rating != null
            ? {
                  label: 'IMDb',
                  value: `★ ${series.rating.toFixed(1)}`,
                  color: 'oklch(0.82 0.18 85)',
              }
            : null,
        showSeasons && series.seasons.length > 0
            ? {
                  label: series.seasons.length === 1 ? 'Season' : 'Seasons',
                  value: String(series.seasons.length),
              }
            : null,
        showTotalEpisodes && series.total_episodes > 0
            ? { label: 'Episodes', value: String(series.total_episodes) }
            : null,
    ].filter(Boolean) as MediaMetaItem[]

    if (series.total_runtime_minutes > 0) {
        const hours = Math.floor(series.total_runtime_minutes / 60)
        items.push({
            label: 'Total runtime',
            value: `${hours.toLocaleString()} ${hours === 1 ? 'hour' : 'hours'}`,
        })
    }

    if (stats && stats.episode_watch_count > 0) {
        const remaining = stats.episodes_remaining
        const percent = Math.floor(stats.progress_percent)
        const hours = Math.floor(stats.total_watch_minutes / 60)
        const watchTime = `${hours.toLocaleString()} ${hours === 1 ? 'hour' : 'hours'}`

        items.push({
            label: 'Eps left',
            value: `${remaining} (${percent}%)`,
        })
        items.push({ label: 'Watch time', value: watchTime })
    }

    return items
}
