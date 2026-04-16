import { Flex, Modal } from '@mantine/core'
import { useState } from 'react'
import { Series } from '../types/series.types'
import { SeasonSelect } from './season-select'
import { SeriesEpisodes } from './series-episodes'

interface Props {
    series: Series
    opened: boolean
    onClose: () => void
}

export function SeriesEpisodesModal({ series, opened, onClose }: Props) {
    const [season, setSeason] = useState(series.seasons[0]?.season ?? 1)

    return (
        <Modal
            opened={opened}
            onClose={onClose}
            size="xl"
            title={
                <Flex gap="1rem" align="center">
                    <SeasonSelect
                        seasons={series.seasons}
                        value={season}
                        onChange={(value) => setSeason(Number(value))}
                        size="sm"
                    />
                    {series.seasons?.[season - 1]?.total} Episodes
                </Flex>
            }
        >
            {opened && <SeriesEpisodes seriesId={series.id} season={season} />}
        </Modal>
    )
}
