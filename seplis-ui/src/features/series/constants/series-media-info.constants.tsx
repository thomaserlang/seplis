import { MediaTypeInfo } from '@/features/media-type/types/media-type-registry.types'
import { SeriesContainer } from '../components/series-container'

export const seriesMediaInfo: MediaTypeInfo = {
    name: 'Series',
    color: 'blue',
    mediaType: 'series',
    render: ({ itemId }) => <SeriesContainer seriesId={Number(itemId)} />,
}
