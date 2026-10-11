import Foundation

nonisolated enum HomeShelf: Int, CaseIterable, Identifiable {
    case watched, toWatch, movieWatchlist, recentSeries, recentMovies
    case popularSeries, popularMovies, recentlyAired, seriesWatchlist
    case unwatchedSeries, unwatchedMovies, favoriteSeries, favoriteMovies

    var id: Int { rawValue }

    var title: String {
        switch self {
        case .watched: "Watched"
        case .toWatch: "Series to Watch"
        case .movieWatchlist: "Movie watchlist"
        case .recentSeries: "Series recently added"
        case .recentMovies: "Movies recently added"
        case .popularSeries: "Popular series"
        case .popularMovies: "Popular movies"
        case .recentlyAired: "Episodes recently aired"
        case .seriesWatchlist: "Series watchlist"
        case .unwatchedSeries: "Series you haven't watched"
        case .unwatchedMovies: "Movies you haven't watched"
        case .favoriteSeries: "Series favorites"
        case .favoriteMovies: "Movie favorites"
        }
    }

    var kind: MediaKind {
        switch self {
        case .movieWatchlist, .recentMovies, .popularMovies, .unwatchedMovies, .favoriteMovies: .movie
        default: .series
        }
    }

    var path: String {
        switch self {
        case .watched: "users/me/watched"
        case .toWatch: "series/to-watch"
        case .recentlyAired: "series/recently-aired"
        default: kind.path
        }
    }

    var query: [URLQueryItem] {
        var values = ["user_can_watch": "true", "per_page": "24"]
        switch self {
        case .movieWatchlist, .seriesWatchlist:
            values["user_watchlist"] = "true"
            values["sort"] = "user_watchlist_added_at_desc"
        case .recentSeries: values["sort"] = "user_play_server_series_added_desc"
        case .recentMovies: values["sort"] = "user_play_server_movie_added_desc"
        case .popularSeries, .popularMovies: values["sort"] = "popularity_desc"
        case .recentlyAired: values["days_ahead"] = "7"
        case .unwatchedSeries, .unwatchedMovies: values["user_has_watched"] = "false"
        case .favoriteSeries, .favoriteMovies:
            values["user_favorites"] = "true"
            values["sort"] = "user_favorite_added_at_desc"
        default: break
        }
        return values.map { URLQueryItem(name: $0.key, value: $0.value) }
    }
}

nonisolated struct HomeItem: Identifiable {
    let reference: MediaReference
    let media: MediaSummary
    var episode: Episode?
    var id: String { "\(reference.kind)-\(reference.id)-\(episode?.number ?? 0)" }
}

nonisolated struct WatchedRecord: Decodable {
    let type: MediaKind
    let data: MediaSummary
}

nonisolated struct SeriesEpisodeRecord: Decodable {
    let series: MediaSummary
    let episode: Episode
}
