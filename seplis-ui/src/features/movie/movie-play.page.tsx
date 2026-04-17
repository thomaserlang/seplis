import { Box } from '@mantine/core'
import { useParams, useSearchParams } from 'react-router-dom'
import { MoviePlayView } from './components/movie-play-view'

export function Component() {
    const { movieId } = useParams<{
        movieId?: string
    }>()
    const [_, setParams] = useSearchParams()
    if (!movieId) throw new Error('Missing movieId')

    const mid = Number(movieId)

    return (
        <Box h="100dvh" w="100dvw">
            <MoviePlayView
                movieId={mid}
                onClose={() =>
                    setParams((params) => {
                        params.delete('pid')
                        return params
                    })
                }
            />
        </Box>
    )
}
