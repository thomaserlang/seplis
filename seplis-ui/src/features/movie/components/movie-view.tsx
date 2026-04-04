import { Flex } from '@mantine/core'
import { Movie } from '../types/movie.types'
import { MovieInfo } from './movie-info'

interface Props {
    movie: Movie
}

export function MovieView({ movie }: Props) {
    return (
        <Flex direction="column" gap="1rem">
            <title>{movie.title}</title>
            <MovieInfo movie={movie} />
        </Flex>
    )
}
