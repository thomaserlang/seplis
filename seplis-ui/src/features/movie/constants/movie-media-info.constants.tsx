import { MediaTypeInfo } from '@/features/media-type/types/media-type-registry.types'
import { MovieContainer } from '../components/movie-container'
import { MovieHoverCard } from '../components/movie-hover-card'
import { Movie } from '../types/movie.types'

export const movieMediaInfo: MediaTypeInfo<Movie> = {
    name: 'Movie',
    color: 'orange',
    mediaType: 'movie',
    render: ({ itemId }) => <MovieContainer movieId={Number(itemId)} />,
    renderHoverCard: ({ data }) => <MovieHoverCard movie={data} />,
}
