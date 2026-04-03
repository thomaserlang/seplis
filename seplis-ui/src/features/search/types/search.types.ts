import { Genre } from '@/types/genre.types'
import { IImage } from '@/types/image.types'

export interface SearchResult {
    type: string
    id: number
    title: string | null
    release_date: string | null
    imdb: string | null
    rating: number | null
    rating_votes: number | null
    poster_image: IImage | null
    genres: Genre[] | null
    seasons: number | null
    episodes: number | null
    runtime: number | null
    language: string | null
}
