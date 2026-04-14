export type MovieUserSortType =
    | 'user_watchlist_added_at_asc'
    | 'user_watchlist_added_at_desc'
    | 'user_favorite_added_at_asc'
    | 'user_favorite_added_at_desc'
    | 'user_last_watched_at_asc'
    | 'user_last_watched_at_desc'
    | 'rating_asc'
    | 'rating_desc'
    | 'popularity_asc'
    | 'popularity_desc'
    | 'release_date_asc'
    | 'release_date_desc'
    | 'user_play_server_movie_added_asc'
    | 'user_play_server_movie_added_desc'

export const MOVIE_SORT_OPTIONS: { value: MovieUserSortType; label: string }[] =
    [
        { value: 'popularity_desc', label: 'Popular' },
        { value: 'release_date_desc', label: 'Newest' },
        { value: 'release_date_asc', label: 'Oldest' },
        { value: 'rating_desc', label: 'Top Rated' },
        { value: 'user_play_server_movie_added_desc', label: 'Recently Added' },
        { value: 'user_last_watched_at_desc', label: 'Recently Watched' },
        { value: 'user_watchlist_added_at_desc', label: 'Watchlist Added' },
        { value: 'user_favorite_added_at_desc', label: 'Favorites Added' },
    ]

export type MovieExpand =
    | 'user_watchlist'
    | 'user_favorite'
    | 'user_can_watch'
    | 'user_rating'
    | 'user_watched'

export interface MoviesGetParams {
    sort?: MovieUserSortType[]
    genre_id?: number[]
    not_genre_id?: number[]
    collection_id?: number[]
    user_can_watch?: boolean
    user_watchlist?: boolean
    user_favorites?: boolean
    user_has_watched?: boolean
    expand?: MovieExpand[]
    release_date_gt?: string
    release_date_lt?: string
    rating_gt?: number
    rating_lt?: number
    rating_votes_gt?: number
    rating_votes_lt?: number
    language?: string[]
}
