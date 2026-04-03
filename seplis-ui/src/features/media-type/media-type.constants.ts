import { seriesMediaInfo } from '@/features/series'
import { movieMediaInfo } from '../movie'
import { MediaType, MediaTypeInfo } from './types/media-type-registry.types'

export const mediaTypes: Record<MediaType, MediaTypeInfo> = {
    series: seriesMediaInfo,
    movie: movieMediaInfo,
}
