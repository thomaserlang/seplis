import Foundation

enum CatalogChoice: String, CaseIterable, Identifiable {
    case any = "Any", yes = "Yes", no = "No"
    var id: String { rawValue }
    var queryValue: String? { self == .any ? nil : String(self == .yes) }
}

struct CatalogFilters: Equatable {
    var sort = "popularity_desc"
    var available: CatalogChoice = .any
    var watchlist: CatalogChoice = .any
    var favorite: CatalogChoice = .any
    var watched: CatalogChoice = .any
    var genres: [Int: CatalogChoice] = [:]
    var languages: Set<String> = []
    var yearFrom = ""
    var yearTo = ""
    var ratingFrom = ""
    var ratingTo = ""
    var votesFrom = ""
    var votesTo = ""

    var validationError: String? {
        for (name, lower, upper, range) in [
            ("Year", yearFrom, yearTo, 1800.0...2200.0),
            ("Rating", ratingFrom, ratingTo, 0.0...10.0),
            ("Votes", votesFrom, votesTo, 0.0...1_000_000_000.0)
        ] {
            for text in [lower, upper] where !text.isEmpty {
                guard let value = Double(text), value.isFinite, range.contains(value),
                      name == "Rating" || value.rounded() == value else { return "Enter a valid \(name.lowercased()) value." }
            }
            if let min = Double(lower), let max = Double(upper), min > max {
                return "\(name): minimum must not exceed maximum."
            }
        }
        return nil
    }

    func query(kind: MediaKind) -> [URLQueryItem] {
        var values = [URLQueryItem(name: "sort", value: sort), .init(name: "per_page", value: "48")]
        for (name, choice) in [("user_can_watch", available), ("user_watchlist", watchlist),
                               ("user_favorites", favorite), ("user_has_watched", watched)] {
            if let value = choice.queryValue { values.append(.init(name: name, value: value)) }
        }
        for id in genres.keys.sorted() {
            if let choice = genres[id], choice != .any {
                values.append(.init(name: choice == .yes ? "genre_id" : "not_genre_id", value: String(id)))
            }
        }
        values += languages.sorted().map { .init(name: "language", value: $0) }
        let date = kind == .movie ? "release_date" : "premiered"
        if let year = Int(yearFrom) { values.append(.init(name: "\(date)_gt", value: "\(year)-01-01")) }
        if let year = Int(yearTo) { values.append(.init(name: "\(date)_lt", value: "\(year)-12-31")) }
        for (name, value) in [("rating_gt", ratingFrom), ("rating_lt", ratingTo),
                              ("rating_votes_gt", votesFrom), ("rating_votes_lt", votesTo)] where !value.isEmpty {
            values.append(.init(name: name, value: value))
        }
        return values
    }

    static func sorts(for kind: MediaKind) -> [(String, String)] {
        let date = kind == .movie ? "release_date" : "premiered"
        return [("Popular", "popularity_desc"), ("Newest", "\(date)_desc"), ("Oldest", "\(date)_asc"),
                ("Top Rated", "rating_desc"), ("Recently Added", "user_play_server_\(kind.rawValue)_added_desc"),
                ("Recently Watched", kind == .movie ? "user_last_watched_at_desc" : "user_last_episode_watched_at_desc"),
                ("Watchlist Added", "user_watchlist_added_at_desc"), ("Favorites Added", "user_favorite_added_at_desc")]
    }
}

nonisolated struct CatalogGenre: Decodable, Identifiable {
    let id: Int
    let name: String
}
