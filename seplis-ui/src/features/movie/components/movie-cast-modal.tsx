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
                        base: 1,
                        xs: 1,
                        sm: 2,
                        md: 2,
                        lg: 3,
                    }}
                />
            )}
        </Modal>
    )
}
