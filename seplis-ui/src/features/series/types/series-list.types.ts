export type SeriesUserSortType =
    | 'user_watchlist_added_at_asc'
    | 'user_watchlist_added_at_desc'
    | 'user_favorite_added_at_asc'
    | 'user_favorite_added_at_desc'
    | 'user_rating_asc'
    | 'user_rating_desc'
    | 'user_last_episode_watched_at_asc'
    | 'user_last_episode_watched_at_desc'
    | 'rating_asc'
    | 'rating_desc'
    | 'popularity_asc'
    | 'popularity_desc'
    | 'user_play_server_series_added_asc'
    | 'user_play_server_series_added_desc'
    | 'premiered_asc'
    | 'premiered_desc'

export const SORT_OPTIONS: { value: SeriesUserSortType; label: string }[] = [
    { value: 'popularity_desc', label: 'Popular' },
    { value: 'premiered_desc', label: 'Newest' },
    { value: 'premiered_asc', label: 'Oldest' },
    { value: 'rating_desc', label: 'Top Rated' },
    { value: 'user_play_server_series_added_desc', label: 'Recently Added' },
    { value: 'user_last_episode_watched_at_desc', label: 'Recently Watched' },
    { value: 'user_watchlist_added_at_desc', label: 'Watchlist Added' },
    { value: 'user_favorite_added_at_desc', label: 'Favorites Added' },
]

export type SeriesExpand =
    | 'user_watchlist'
    | 'user_favorite'
    | 'user_can_watch'
    | 'user_last_episode_watched'
    | 'user_rating'

export interface SeriesListGetParams {
    sort?: SeriesUserSortType[]
    genre_id?: number[]
    not_genre_id?: number[]
    user_can_watch?: boolean
    user_watchlist?: boolean
    user_favorites?: boolean
    user_has_watched?: boolean
    expand?: SeriesExpand[]
    premiered_gt?: string
    premiered_lt?: string
    rating_gt?: number
    rating_lt?: number
    rating_votes_gt?: number
    rating_votes_lt?: number
    language?: string[]
}
