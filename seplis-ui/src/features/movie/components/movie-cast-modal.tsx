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
            {opened && (
                <MovieCast
                    movieId={movieId}
                    cols={{
                        base: 2,
                        xs: 3,
                        sm: 4,
                        md: 5,
                    }}
                />
            )}
        </Modal>
    )
}
