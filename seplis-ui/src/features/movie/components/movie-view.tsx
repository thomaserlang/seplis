import { Movie } from '../types/movie.types'
import { MovieInfo } from './movie-info'

interface Props {
    movie: Movie
}

export function MovieView({ movie }: Props) {
    return <MovieInfo movie={movie} />
}
