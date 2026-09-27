import Foundation

nonisolated struct Season: Decodable, Identifiable {
    let season: Int
    let total: Int
    var id: Int { season }
}

nonisolated struct Episode: Decodable, Identifiable {
    let number: Int
    let title: String?
    let season: Int?
    let episode: Int?
    let plot: String?
    let runtime: Int?
    let airDate: String?
    let userWatched: Watched?
    let userCanWatch: WatchAvailability?
    var id: Int { number }
    var canPlay: Bool { userCanWatch?.onPlayServer != false }
    var watchHeading: String { (userWatched?.position ?? 0) > 0 ? "Continue watching" : "Next to watch" }
    var numberLabel: String {
        if let season, let episode { "S\(season) E\(episode)" } else { "Episode \(number)" }
    }
    var label: String { title.map { "\(numberLabel) - \($0)" } ?? numberLabel }
}
