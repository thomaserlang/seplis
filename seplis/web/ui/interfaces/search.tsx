import { IImage } from "./image"

export interface ITitleSearchResult {
    type: string
    id: number
    title: string | null
    release_date: string | null
    imdb: string | null
    poster_image: IImage | null
  }