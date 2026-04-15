import { MediaTypeInfo } from '@/features/media-type/types/media-type-registry.types'
import { MovieContainer } from '../components/movie-container'
import { MovieHoverCard } from '../components/movie-hover-card'
import { MoviePlayView } from '../components/movie-play-view'
import { Movie } from '../types/movie.types'

export const movieMediaInfo: MediaTypeInfo<Movie> = {
    name: 'Movie',
    color: 'orange',
    mediaType: 'movie',
    accentHue: 30,
    render: ({ itemId }) => <MovieContainer movieId={Number(itemId)} />,
    renderHoverCard: ({ data }) => <MovieHoverCard movie={data} />,
    player: ({ itemId, onClose }) => (
        <MoviePlayView movieId={Number(itemId)} onClose={onClose} />
    ),
}
