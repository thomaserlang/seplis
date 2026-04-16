import { Modal } from '@mantine/core'
import { MovieCast } from './movie-cast'

interface Props {
    movieId: number
    opened: boolean
    onClose: () => void
}

export function MovieCastModal({ movieId, opened, onClose }: Props) {
    return (
        <Modal opened={opened} onClose={onClose} size="xl" title="Cast">
            {opened && <MovieCast movieId={movieId} loadMoreButton />}
        </Modal>
    )
}
