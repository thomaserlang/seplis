import { Box } from '@mantine/core'
import { useNavigate, useParams } from 'react-router-dom'
import { useGetMovie } from './api/movie.api'
import { MoviePlayView } from './components/movie-play-view'

export function Component() {
    const { movieId } = useParams<{
        movieId?: string
    }>()
    const navigate = useNavigate()
    if (!movieId) throw new Error('Missing movieId')

    const mid = Number(movieId)
    const { data: movie } = useGetMovie({ movieId: mid })

    return (
        <Box h="100dvh" w="100dvw">
            <MoviePlayView
                movieId={mid}
                title={movie?.title}
                onClose={() => navigate(-1)}
            />
        </Box>
    )
}
