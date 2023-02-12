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


export interface IEpisodeWatched {
    episode_number: number
    times: number
    position: number
    watched_at: string | null
}
export function IEpisodeWatchedDefault(EpisodeNumber: number): IEpisodeWatched {
    return {
        episode_number: EpisodeNumber,
        times: 0,
        position: 0,
        watched_at: null,
    }
}


export interface IUserCanWatchEpisode {
    on_play_server: boolean
}


export interface IEpisode {
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
    user_watched: IEpisodeWatched | null
    user_can_watch: IUserCanWatchEpisode | null
}


export interface IEpisodeWatchedIncrement {
    watched_at: Date
}