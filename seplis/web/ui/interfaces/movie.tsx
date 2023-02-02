import { IGenre } from "./genre"
import { IImage } from "./image"
import { TExternals } from "./types"

export interface IMovie {
    id: number
    poster_image: IImage | null
    title: string | null
    original_title: string | null
    alternative_titles: string[]
    status: number | null
    plot: string | null
    tagline: string | null
    externals: TExternals
    language: string | null
    runtime: number | null
    release_date: string | null
    budget: number | null
    revenue: number | null
    popularity: number | null
    rating: number | null
    genres: IGenre[]
}


export interface IMovieStared {
    stared: boolean
    created_at: string
}