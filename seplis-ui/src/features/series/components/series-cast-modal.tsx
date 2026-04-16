import { Modal } from '@mantine/core'
import { SeriesCast } from './series-cast'

interface Props {
    seriesId: number
    opened: boolean
    onClose: () => void
}

export function SeriesCastModal({ seriesId, opened, onClose }: Props) {
    return (
        <Modal opened={opened} onClose={onClose} size="xl" title="Cast">
            {opened && <SeriesCast seriesId={seriesId} loadMoreButton />}
        </Modal>
    )
}
