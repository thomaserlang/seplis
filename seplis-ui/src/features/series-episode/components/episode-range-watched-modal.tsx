import { Modal } from '@mantine/core'
import { SeriesSeason } from '../types/series-season.types'
import { EpisodeRangeWatchedForm } from './episode-range-watched-form'

interface Props {
    opened: boolean
    onClose: () => void
    seriesId: number
    season: number
    seasons: SeriesSeason[]
}

export function EpisodeRangeWatchedModal({
    opened,
    onClose,
    seriesId,
    season,
    seasons,
}: Props) {
    return (
        <Modal
            opened={opened}
            onClose={onClose}
            title="Mark watched range"
            centered
        >
            <EpisodeRangeWatchedForm
                onClose={onClose}
                seriesId={seriesId}
                season={season}
                seasons={seasons}
            />
        </Modal>
    )
}
