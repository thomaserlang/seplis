import { EpisodesModal } from '@/features/series-episode'
import { Button, Flex, Text } from '@mantine/core'
import { ListIcon } from '@phosphor-icons/react'
import { UsersIcon } from '@phosphor-icons/react/dist/ssr'
import { useState } from 'react'
import { Series } from '../types/series.types'
import { SeriesCast } from './series-cast'
import { SeriesCastModal } from './series-cast-modal'
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
                <SeriesInfo series={series} />
                <Flex gap="0.5rem" p="1rem" direction="column">
                    <Flex gap="0.5rem">
                        <Button
                            variant="default"
                            leftSection={<ListIcon />}
                            onClick={() => setModal('episodes')}
                        >
                            Episodes
                        </Button>
                        <Button
                            variant="default"
                            leftSection={<UsersIcon />}
                            onClick={() => setModal('cast')}
                        >
                            Cast
                        </Button>
                    </Flex>
                    <SeriesCast
                        seriesId={series.id}
                        maxCast={14}
                        title={
                            <Text size="md" fw="600">
                                Top Cast
                            </Text>
                        }
                    />
                </Flex>
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
