import { Movie } from '@/features/movie'
import { Series } from '@/features/series'

export interface UserWatched {
    type: string
    data: Movie | Series
}
