import Foundation

nonisolated struct Series: Decodable, Identifiable {
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
    let premiered: String?
    let ended: String?
    let totalEpisodes: Int?
    let seasons: [Season]?
    let userWatchlist: Watchlist?
    let userFavorite: Favorite?

    var displayTitle: String { title ?? originalTitle ?? "Untitled" }
}
