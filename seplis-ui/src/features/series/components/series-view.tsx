import { EpisodesModal, RandomEpisodeButton } from '@/features/series-episode'
import { Button, Flex, Text } from '@mantine/core'
import { ListIcon } from '@phosphor-icons/react'
import { useState } from 'react'
import { Series } from '../types/series.types'
import { SeriesCastModal } from './series-cast-modal'
import { SeriesCastSlider } from './series-cast-slider'
import { SeriesInfo } from './series-info'

interface Props {
    series: Series
}

export function SeriesView({ series }: Props) {
    const [modal, setModal] = useState<'episodes' | 'cast' | undefined>(
        undefined,
    )

    return (
        <>
            <Flex direction="column">
                <title>{series.title}</title>
                <SeriesInfo series={series}>
                    <Flex gap="0.5rem" direction="column">
                        <Flex gap="0.5rem" wrap="wrap" align="center">
                            <Button
                                variant="default"
                                size="compact-md"
                                leftSection={<ListIcon />}
                                onClick={() => setModal('episodes')}
                            >
                                Episodes
                            </Button>
                            <RandomEpisodeButton
                                seriesId={series.id}
                                totalEpisodes={series.total_episodes}
                            />
                        </Flex>

                        <SeriesCastSlider
                            seriesId={series.id}
                            maxCast={22}
                            background="var(--card)"
                            title={
                                <Text
                                    onClick={() => setModal('cast')}
                                    size="md"
                                    fw="700"
                                    style={{ cursor: 'pointer' }}
                                >
                                    Top Cast
                                </Text>
                            }
                            onClick={() => setModal('cast')}
                        />
                    </Flex>
                </SeriesInfo>
            </Flex>

            <EpisodesModal
                seriesId={series.id}
                seasons={series.seasons}
                opened={modal === 'episodes'}
                onClose={() => setModal(undefined)}
            />

            <SeriesCastModal
                seriesId={series.id}
                opened={modal === 'cast'}
                onClose={() => setModal(undefined)}
            />
        </>
    )
}
