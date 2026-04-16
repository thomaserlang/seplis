import { Flex, Modal } from '@mantine/core'
import { useState } from 'react'
import { SeriesEpisodes } from '../components/series-episodes'
import { SeriesSeason } from '../types/series-season.types'
import { SeasonSelect } from './season-select'

interface Props {
    seriesId: number
    seasons: SeriesSeason[]
    opened: boolean
    onClose: () => void
}

export function SeriesEpisodesModal({
    seriesId,
    seasons,
    opened,
    onClose,
}: Props) {
    const [season, setSeason] = useState(seasons[0]?.season ?? 1)

    return (
        <Modal
            opened={opened}
            onClose={onClose}
            size="xl"
            title={
                <Flex gap="1rem" align="center">
                    <SeasonSelect
                        seasons={seasons}
                        value={season}
                        onChange={(value) => setSeason(Number(value))}
                        size="sm"
                    />
                    {seasons?.[season - 1]?.total} Episodes
                </Flex>
            }
        >
            {opened && <SeriesEpisodes seriesId={seriesId} season={season} />}
        </Modal>
    )
}
