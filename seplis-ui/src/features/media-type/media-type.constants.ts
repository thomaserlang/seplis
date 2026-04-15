import { movieMediaInfo } from '@/features/movie/constants/movie-media-info.constants'
import { episodeMediaInfo } from '@/features/series-episode/constants/episode-media-info.constants'
import { seriesMediaInfo } from '@/features/series/constants/series-media-info.constants'
import { MediaType, MediaTypeInfo } from './types/media-type-registry.types'

export const mediaTypes: Record<MediaType, MediaTypeInfo> = {
    series: seriesMediaInfo,
    episode: episodeMediaInfo,
    movie: movieMediaInfo,
}
