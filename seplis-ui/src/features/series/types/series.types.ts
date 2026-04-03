import { Genre } from '@/types/genre.types'
import { IImage } from '@/types/image.types'
import { Episode, UserCanWatchEpisode } from './episodes.types'

export interface Series {
    id: number
    title: string | null
    original_title: string | null
    alternative_titles: string[]
    externals: { [key: string]: string }
    plot: string | null
    tagline: string | null
    premiered: string | null
    ended: string | null
    importers: SeriesImporters
    runtime: number | null
    genres: Genre[]
    episode_type: number | null
    language: string | null
    created_at: string
    updated_at: string | null
    status: number
    seasons: SeriesSeason[]
    total_episodes: number
    poster_image: IImage | null
    popularity: number | null
    rating: number | null
    user_watchlist: SeriesWatchlist | null
    user_favorite: SeriesFavorite | null
    user_last_episode_watched: Episode | null
    user_rating: SeriesUserRating | null
    user_can_watch: UserCanWatchEpisode | null
}

export interface SeriesImporters {
    info: string | null
    episodes: string | null
}

export interface SeriesUserRatingUpdate {
    rating: number
}

export interface SeriesUserRating {
    rating: number | null
}

export interface SeriesSeason {
    season: number
    from: number
    to: number
    total: number
}

export interface SeriesUserStats {
    episodes_watched: number
    episodes_watched_minutes: number
}

export interface SeriesWatchlist {
    on_watchlist: boolean
    created_at: string | null
}

export interface SeriesFavorite {
    favorite: boolean
    created_at: string | null
}

export interface SeriesUserSettings {
    subtitle_lang: string | null
    audio_lang: string | null
}

export interface SeriesWithEpisodes extends Series {
    episodes: Episode[]
}

export interface SeriesAndEpisode {
    series: Series
    episode: Episode
}

export interface SeriesAirDates {
    air_date: Date
    series: SeriesWithEpisodes[]
}
