import { IImage } from './image'
import { IGenre } from './genre'
import { TExternals } from './types'
import { IEpisode, IEpisodeCreate, IEpisodeWatched } from './episode'


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


export interface ISeriesCreate {
    title: string | null
    original_title: string | null
    alternative_titles: string[] | null
    externals: TExternals | null
    status: number | null
    plot: string | null
    tagline: string | null
    premiered: string | null
    ended: string | null
    importers: ISeriesImporters | null
    runtime: number | null
    genres: (string | number)[] | null
    episode_type: number | null
    language: string | null
    poster_image_id: number | null
    popularity: number | null
    rating: number | null
    episodes: IEpisodeCreate[] | null
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
}


export interface ISeriesUserStats {
    episodes_watched: number
    episodes_watched_minutes: number
}


export interface ISeriesFollowing {
    following: boolean
    created_at: string | null
}


export interface ISeriesUser {
    series: ISeries
    rating: number | null
    following: boolean
    last_episode_watched: IEpisode | null
    last_episode_watched_data: IEpisodeWatched | null
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