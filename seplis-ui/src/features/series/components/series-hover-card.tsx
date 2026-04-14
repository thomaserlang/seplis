import { MediaInfoHoverCard } from '@/components/media-info'
import { mediaTypes } from '@/features/media-type'
import { EpisodeToWatchCard } from '@/features/series-episode'
import { Box, Flex } from '@mantine/core'
import { useSearchParams } from 'react-router-dom'
import { Series } from '../types/series.types'
import { SeriesFavoriteButton } from './series-favorite-button'
import { SeriesMetaItems } from './series-info'
import { SeriesWatchlistButton } from './series-watchlist-button'

interface Props {
    series: Series
}

export function SeriesHoverCard({ series }: Props) {
    const [_, setParams] = useSearchParams()

    const handleClick = () => {
        setParams((params) => {
            params.set('mid', `series-${series.id}`)
            return params
        })
    }

    return (
        <MediaInfoHoverCard
            poster={series.poster_image}
            accentHue={mediaTypes['series'].accentHue}
            title={series.title || series.original_title || 'Untitled'}
            metaItems={SeriesMetaItems({
                series,
                showYearRange: true,
                showRuntime: true,
                showLanguage: true,
                showRating: true,
            })}
            genres={series.genres}
            onInfoClick={handleClick}
        >
            <Flex gap="0.5rem" direction="column">
                <Flex gap="0.5rem" wrap="wrap">
                    <Box style={{ flex: '1 1 18rem' }} miw="0">
                        <EpisodeToWatchCard
                            seriesId={series.id}
                            buttonSize="compact-sm"
                            fz="xs"
                            size="sm"
                        />
                    </Box>
                </Flex>
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
            </Flex>
        </MediaInfoHoverCard>
    )
}
