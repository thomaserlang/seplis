import { MediaTypeInfo } from '@/features/media-type/types/media-type-registry.types'
import { SeriesContainer } from '../components/series-container'
import { SeriesHoverCard } from '../components/series-hover-card'
import { Series } from '../types/series.types'

export const seriesMediaInfo: MediaTypeInfo<Series> = {
    name: 'Series',
    color: 'blue',
    mediaType: 'series',
    render: ({ itemId }) => <SeriesContainer seriesId={Number(itemId)} />,
    renderHoverCard: ({ data }) => <SeriesHoverCard series={data} />,
}
