import { Box } from '@mantine/core'
import { useParams } from 'react-router-dom'
import { MoviePlayView } from './components/movie-play-view'

export function Component() {
    const { movieId } = useParams<{
        movieId?: string
    }>()
    if (!movieId) throw new Error('Missing movieId')

    return (
        <Box h="100dvh" w="100dvw">
            <MoviePlayView movieId={Number(movieId)} />
        </Box>
    )
}
