import Foundation

nonisolated struct Movie: Decodable, Identifiable {
    let id: Int
    let title: String?
    let originalTitle: String?
    let tagline: String?
    let status: Int?
    let plot: String?
    let posterImage: Poster?
    let genres: [Genre]?
    let runtime: Int?
    let rating: Double?
    let language: String?
    let releaseDate: String?
    let budget: Int?
    let revenue: Int?
    let userWatched: Watched?
    let userWatchlist: Watchlist?
    let userFavorite: Favorite?
    let collection: MovieCollection?

    var displayTitle: String { title ?? originalTitle ?? "Untitled" }
}

nonisolated struct MovieCollection: Decodable, Identifiable {
    let id: Int
    let name: String
}
