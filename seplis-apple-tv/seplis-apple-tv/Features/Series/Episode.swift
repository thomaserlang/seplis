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
    func formattedAirDate(locale: Locale = .current, timeZone: TimeZone = .current) -> String? {
        guard let airDate else { return nil }
        let parser = DateFormatter()
        parser.locale = Locale(identifier: "en_US_POSIX")
        parser.timeZone = timeZone
        parser.dateFormat = "yyyy-MM-dd"
        parser.isLenient = false
        guard let date = parser.date(from: airDate) else { return airDate }

        let formatter = DateFormatter()
        formatter.locale = locale
        formatter.timeZone = timeZone
        formatter.dateStyle = .medium
        return formatter.string(from: date)
    }
    var numberLabel: String {
        if let season, let episode { "S\(season) E\(episode)" } else { "Episode \(number)" }
    }
    var label: String { title.map { "\(numberLabel) - \($0)" } ?? numberLabel }
}
