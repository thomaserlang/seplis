import Foundation

nonisolated struct Watchlist: Decodable {
    let onWatchlist: Bool
}

nonisolated struct Favorite: Decodable {
    let favorite: Bool
}

nonisolated struct Watched: Decodable {
    let times: Int
    let position: Int
}

nonisolated struct WatchAvailability: Decodable {
    let onPlayServer: Bool
}
