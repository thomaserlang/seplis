import { MediaInfoHoverCard } from '@/components/media-info'
import { EpisodeToWatchCard } from '@/features/series-episode'
import { Box, Flex } from '@mantine/core'
import { Series } from '../types/series.types'
import { SeriesFavoriteButton } from './series-favorite-button'
import { SeriesMetaItems } from './series-info'
import { SeriesWatchlistButton } from './series-watchlist-button'

interface Props {
    series: Series
}

export function SeriesHoverCard({ series }: Props) {
    return (
        <MediaInfoHoverCard
            posterUrl={series.poster_image?.url}
            title={series.title || series.original_title || 'Untitled'}
            metaItems={SeriesMetaItems({
                series,
                showYearRange: true,
                showRuntime: true,
                showLanguage: true,
                showRating: true,
            })}
            genres={series.genres}
        >
            <Flex gap="0.5rem" direction="column">
                <Flex gap="0.5rem" wrap="wrap">
                    <SeriesWatchlistButton
                        seriesId={series.id}
                        size="compact-sm"
                    />
                    <SeriesFavoriteButton
                        seriesId={series.id}
                        size="compact-sm"
                    />
                </Flex>
                <Flex gap="0.5rem" wrap="wrap">
                    <Box style={{ flex: '1 1 18rem' }} miw="0">
                        <EpisodeToWatchCard
                            seriesId={series.id}
                            buttonSize="compact-sm"
                            fz="xs"
                        />
                    </Box>
                </Flex>
            </Flex>
        </MediaInfoHoverCard>
    )
}
