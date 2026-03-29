import { IImage } from './image'
import { IGenre } from './genre'
import { TExternals } from './types'
import { IEpisode, IEpisodeCreate, IEpisodeWatched, IUserCanWatchEpisode } from './episode'


export interface ISeriesImporters {
    info: string | null
    episodes: string | null
}


export interface ISeriesUserRatingUpdate {
    rating: number
}


export interface ISeriesUserRating {
    rating: number | null
}


export interface ISeriesRequest {
    title?: string | null
    original_title?: string | null
    alternative_titles?: string[] | null
    externals?: TExternals | null
    status?: number | null
    plot?: string | null
    tagline?: string | null
    premiered?: string | null
    ended?: string | null
    importers?: ISeriesImporters | null
    runtime?: number | null
    genres?: (string | number)[] | null
    episode_type?: number | null
    language?: string | null
    poster_image_id?: number | null
    popularity?: number | null
    rating?: number | null
    rating_votes?: number | null
    episodes?: IEpisodeCreate[] | null
}


export interface ISeriesSeason {
    season: number
    from: number
    to: number
    total: number
}


export interface ISeries {
    id: number
    title: string | null
    original_title: string | null
    alternative_titles: string[]
    externals: TExternals
    plot: string | null
    tagline: string | null
    premiered: string | null
    ended: string | null
    importers: ISeriesImporters
    runtime: number | null
    genres: IGenre[]
    episode_type: number | null
    language: string | null
    created_at: string
    updated_at: string | null
    status: number
    seasons: ISeriesSeason[]
    total_episodes: number
    poster_image: IImage | null
    popularity: number | null
    rating: number | null
    user_watchlist: ISeriesWatchlist | null
    user_favorite: ISeriesFavorite | null
    user_last_episode_watched: IEpisode | null
    user_rating: ISeriesUserRating | null
    user_can_watch: IUserCanWatchEpisode | null
}


export interface ISeriesUserStats {
    episodes_watched: number
    episodes_watched_minutes: number
}


export interface ISeriesWatchlist {
    on_watchlist: boolean
    created_at: string | null
}


export interface ISeriesFavorite {
    favorite: boolean
    created_at: string | null
}


export interface ISeriesUserSettings {
    subtitle_lang: string | null
    audio_lang: string | null
}


export interface ISeriesWithEpisodes extends ISeries {
    episodes: IEpisode[]
}


export interface ISeriesAndEpisode {
    series: ISeries
    episode: IEpisode
}


export interface ISeriesAirDates {
    air_date: Date
    series: ISeriesWithEpisodes[]
}


export interface ISeriesWatchlist {
    on_watchlist: boolean
    created_at: string
}


export interface ISeriesFavorite {
    favorite: boolean
    created_at: string
}