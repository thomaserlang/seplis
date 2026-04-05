import { MediaInfo, MediaMetaItem, MediaStatus } from '@/components/media-info'
import {
    EpisodeLastWatchedCard,
    EpisodeToWatchCard,
} from '@/features/series-episode'
import { langCodeToLang } from '@/utils/language.utils'
import { Flex } from '@mantine/core'
import { Series } from '../types/series.types'
import { SeriesFavoriteButton } from './series-favorite-button'
import { SeriesWatchlistButton } from './series-watchlist-button'

interface Props {
    series: Series
}

const STATUS: Record<number, MediaStatus> = {
    0: { label: 'Unknown', dot: 'oklch(0.6 0 0)' },
    1: { label: 'Returning', dot: 'oklch(0.7 0.17 175)' },
    2: { label: 'Ended', dot: 'oklch(0.6 0.2 25)' },
    3: { label: 'Cancelled', dot: 'oklch(0.7 0.18 55)' },
    4: { label: 'In production', dot: 'oklch(0.6 0.2 250)' },
    5: { label: 'Planned', dot: 'oklch(0.55 0.22 295)' },
}

export function SeriesInfo({ series }: Props) {
    const startYear = series.premiered?.substring(0, 4)
    const endYear = series.ended?.substring(0, 4)
    const yearRange = startYear
        ? endYear && endYear !== startYear
            ? `${startYear}–${endYear}`
            : startYear
        : null

    const metaItems: MediaMetaItem[] = [
        yearRange ? { label: 'Year', value: yearRange } : null,
        series.runtime
            ? { label: 'Runtime', value: `${series.runtime} min / ep` }
            : null,
        series.language
            ? { label: 'Language', value: langCodeToLang(series.language) }
            : null,
        series.rating != null
            ? {
                  label: 'IMDb',
                  value: `★ ${series.rating.toFixed(1)}`,
                  color: 'oklch(0.82 0.18 85)',
              }
            : null,
        series.seasons.length > 0
            ? {
                  label: series.seasons.length === 1 ? 'Season' : 'Seasons',
                  value: String(series.seasons.length),
              }
            : null,
        series.total_episodes > 0
            ? { label: 'Episodes', value: String(series.total_episodes) }
            : null,
    ].filter(Boolean) as MediaMetaItem[]

    return (
        <MediaInfo
            posterUrl={
                series.poster_image
                    ? `${series.poster_image.url}@SX320.webp`
                    : undefined
            }
            accentHue={250}
            status={series.status != null ? STATUS[series.status] : undefined}
            title={series.title || series.original_title || 'Unknown title'}
            originalTitle={series.original_title}
            tagline={series.tagline}
            metaItems={metaItems}
            genres={series.genres}
            plot={series.plot}
            renderMainButtons={() => (
                <Flex gap="1rem" direction="column">
                    <Flex gap="0.5rem" wrap="wrap">
                        <SeriesWatchlistButton seriesId={series.id} />
                        <SeriesFavoriteButton seriesId={series.id} />
                    </Flex>
                    <Flex gap="1rem" wrap="wrap">
                        <EpisodeToWatchCard seriesId={series.id} />
                        <EpisodeLastWatchedCard seriesId={series.id} />
                    </Flex>
                </Flex>
            )}
        />
    )
}
