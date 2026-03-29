import { IGenre } from './genre'
import { IImage } from './image'

export interface ITitleSearchResult {
    type: string
    id: number
    title: string | null
    release_date: string | null
    imdb: string | null
    rating: number | null
    rating_votes: number | null
    poster_image: IImage | null
    genres: IGenre[] | null
    seasons: number | null
    episodes: number | null
    runtime: number | null
    language: string | null
  }