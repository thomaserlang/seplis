import { MediaType } from '@/features/media-type'
import { Movie } from '@/features/movie'
import { Series } from '@/features/series'

export interface UserWatched {
    type: MediaType
    data: Movie | Series
    series: Series
    movie: Movie
}
