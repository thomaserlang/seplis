import { IGenre } from "./genre"
import { IImage } from "./image"
import { IMovieCollection } from "./movie-collection"
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
    rating_votes: number | null
    collection: IMovieCollection | null
    genres: IGenre[]
    user_watched: IMovieWatched
}


export interface IMovieWatched {
    times: number
    position: number
    watched_at: string
}
export function IMovieWatchedDefault(EpisodeNumber: number): IMovieWatched {
    return {
        times: 0,
        position: 0,
        watched_at: null,
    }
}


export interface IMovieWatchlist {
    on_watchlist: boolean
    created_at: string
}

export interface IMovieFavorite {
    favorite: boolean
    created_at: string
}


export interface IEventMovieWatched {
    movieId: number
    watched: IMovieWatched
}