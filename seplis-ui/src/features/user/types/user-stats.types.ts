export interface UserSeriesStats {
    series_watchlist: number
    series_watched: number
    series_finished: number
    episodes_watched: number
    episodes_watched_minutes: number
}

export interface UserMovieStats {
    movies_watched: number
    movie_watch_count: number
    movies_watchlist: number
    total_watch_minutes: number
}

export interface UserWatchActivityPeriod {
    date: string
    episodes_watched: number
    movies_watched: number
    series_minutes: number
    movie_minutes: number
}
