import { IImage } from './image'
import { IGenre } from './genre'


export interface IEpisodeCreate {
    title: string
    original_title: string | null
    number: number
    season: number | null
    episode: number | null
    air_date: Date | null
    air_datetime: Date | null
    plot: string | null
    runtime: number | null
    rating: number | null
}
  

export interface IEpisodeUpdate extends IEpisodeCreate {
    title: string | null
}


export interface IEpisode {
    title: string | null
    number: number
    season: number | null
    plot: string | null
    runtime: number | null
    rating: number | null
}

export interface IEpisodeWatchedIncrement {
    watched_at: Date
}


export interface IEpisodeWatched {
    episode_number: number
    times: number
    position: number
    watched_at: Date | null
}


export interface IEpisodeWithUserWatched extends IEpisode {
    user_watched: IEpisodeWatched | null
}


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
    externals: { [key: string]: string | null } | null
    status: number | null
    plot: string | null
    tagline: string | null
    premiered: Date | null
    ended: Date | null
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

export interface ISeries {
    id: number
    title: string | null
    alternative_titles: string[]
    externals: { [key: string]: string }
    plot: string | null
    tagline: string | null
    premiered: Date | null
    ended: Date | null
    importers: ISeriesImporters
    runtime: number | null
    genres: IGenre[]
    episode_type: number | null
    language: string | null
    created_at: Date
    updated_at: Date | null
    status: number
    seasons: { [key: string]: any }[]
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
    created_at: Date | null
}


type ISeriesUserSortType =
    | 'followed_at_asc'
    | 'followed_at_desc'
    | 'user_rating_asc'
    | 'user_rating_desc'
    | 'watched_at_asc'
    | 'watched_at_desc'


export interface ISeriesUser {
    series: ISeries
    rating: number | null
    following: boolean
    last_episode_watched: IEpisode | null
    last_episode_watched_data: IEpisodeWatched | null
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