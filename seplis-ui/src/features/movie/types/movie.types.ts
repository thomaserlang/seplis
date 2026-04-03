import { Genre } from '@/types/genre.types'
import { IImage } from '@/types/image.types'
import { MovieCollection } from './movie-collection.types'

export interface Movie {
    id: number
    poster_image: IImage | null
    title: string | null
    original_title: string | null
    alternative_titles: string[]
    status: number | null
    plot: string | null
    tagline: string | null
    externals: { [key: string]: string }
    language: string | null
    runtime: number | null
    release_date: string | null
    budget: number | null
    revenue: number | null
    popularity: number | null
    rating: number | null
    rating_votes: number | null
    collection: MovieCollection | null
    genres: Genre[]
    user_watched: MovieWatched
}

export interface MovieWatched {
    times: number
    position: number
    watched_at: string
}

export interface MovieWatchlist {
    on_watchlist: boolean
    created_at: string
}

export interface MovieFavorite {
    favorite: boolean
    created_at: string
}

export interface EventMovieWatched {
    movieId: number
    watched: MovieWatched
}
