import { MediaTypeInfo } from '@/features/media-type/types/media-type-registry.types'
import { MovieContainer } from '../components/movie-container'

export const movieMediaInfo: MediaTypeInfo = {
    name: 'Movie',
    color: 'orange',
    mediaType: 'movie',
    render: ({ itemId }) => <MovieContainer movieId={Number(itemId)} />,
}
