export interface Episode {
    title: string | null
    original_title: string | null
    number: number
    season: number | null
    episode: number | null
    plot: string | null
    runtime: number | null
    rating: number | null
    air_date: string | null
    air_datetime: string | null
    user_watched: EpisodeWatched | null
    user_can_watch: UserCanWatchEpisode | null
}

export interface EpisodeWatched {
    episode_number: number
    times: number
    position: number
    watched_at: string | null
}

export function EpisodeWatchedDefault(EpisodeNumber: number): EpisodeWatched {
    return {
        episode_number: EpisodeNumber,
        times: 0,
        position: 0,
        watched_at: null,
    }
}

export interface UserCanWatchEpisode {
    on_play_server: boolean
}
