import { Box, Button, Flex, Modal, Text } from '@mantine/core'
import { useState } from 'react'
import { SeriesSeason } from '../types/series-season.types'
import { EpisodeRangeWatchedTrigger } from './episode-range-watched-trigger'
import { Episodes } from './episodes'
import { SeasonSelect } from './season-select'

interface Props {
    seriesId: number
    seasons: SeriesSeason[]
    opened: boolean
    onClose: () => void
}

export function EpisodesModal({ seriesId, seasons, opened, onClose }: Props) {
    const [season, setSeason] = useState(seasons[0]?.season ?? 1)
    const currentSeason = seasons.find((item) => item.season === season)

    return (
        <Modal
            opened={opened}
            onClose={onClose}
            size="xl"
            title={
                <Flex gap="1rem" align="center" wrap="wrap">
                    <SeasonSelect
                        seasons={seasons}
                        value={season}
                        onChange={(value) => setSeason(Number(value))}
                        size="xs"
                    />
                    <Text span size="sm" fw={600}>
                        {currentSeason?.total ?? 0} Episodes
                    </Text>
                    <Box ml="auto" mr="0.5rem">
                        <EpisodeRangeWatchedTrigger
                            seriesId={seriesId}
                            season={season}
                            seasons={seasons}
                        >
                            <Button
                                variant="default"
                                size="xs"
                                disabled={!currentSeason?.total}
                            >
                                Mark range watched
                            </Button>
                        </EpisodeRangeWatchedTrigger>
                    </Box>
                </Flex>
            }
        >
            {opened && <Episodes seriesId={seriesId} season={season} />}
        </Modal>
    )
}
