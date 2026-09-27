import Foundation

nonisolated enum MediaKind: String, Decodable, Hashable {
    case movie, series
    var path: String { self == .movie ? "movies" : "series" }
}

nonisolated struct MediaReference: Hashable {
    let kind: MediaKind
    let id: Int
    var path: String { "\(kind.path)/\(id)" }
}

nonisolated struct Poster: Decodable {
    let url: String
    var imageURL: URL? { URL(string: "\(url)@SX320.webp") }
}

nonisolated struct Genre: Decodable {
    let name: String
}

// Movies and series share these catalog fields; season data is present only for series.
nonisolated struct Media: Decodable, Identifiable {
    let id: Int
    let title: String?
    let plot: String?
    let posterImage: Poster?
    let genres: [Genre]?
    let runtime: Int?
    let rating: Double?
    let releaseDate: String?
    let premiered: String?
    let seasons: [Season]?
    let userWatched: Watched?
    let userWatchlist: Watchlist?
    let userFavorite: Favorite?
    let collection: MovieCollection?

    var displayTitle: String { title ?? "Untitled" }
    var metadata: String {
        var parts: [String] = []
        if let date = releaseDate ?? premiered { parts.append(String(date.prefix(4))) }
        if let runtime, runtime > 0 { parts.append("\(runtime) min") }
        parts += (genres ?? []).map(\.name)
        return parts.joined(separator: " · ")
    }
}

nonisolated struct MovieCollection: Decodable, Identifiable {
    let id: Int
    let name: String
}
