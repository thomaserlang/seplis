import { MediaTypeInfo } from '@/features/media-type'

export const movieMediaInfo: MediaTypeInfo = {
    name: 'Movie',
    color: 'blue',
    mediaType: 'movie',
    render: () => <div>Render movie</div>,
}
