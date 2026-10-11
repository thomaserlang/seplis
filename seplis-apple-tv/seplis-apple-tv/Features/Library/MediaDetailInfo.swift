import Foundation

nonisolated struct MediaDetailFact: Equatable {
    let label: String
    let value: String
}

protocol MediaDetailInfo {
    var displayTitle: String { get }
    var originalTitle: String? { get }
    var tagline: String? { get }
    var plot: String? { get }
    var posterImage: Poster? { get }
    var genres: [Genre]? { get }
    var userWatchlist: Watchlist? { get }
    var userFavorite: Favorite? { get }
    var statusLabel: String? { get }
    var detailFacts: [MediaDetailFact] { get }
}

enum MediaFactFormat {
    static func language(_ code: String) -> String {
        let language = String(code.split(separator: "-").first ?? Substring(code))
        return Locale(identifier: "en").localizedString(forLanguageCode: language) ?? code
    }

    static func money(_ amount: Int) -> String {
        if amount >= 1_000_000_000 { return String(format: "$%.1fB", Double(amount) / 1_000_000_000) }
        if amount >= 1_000_000 { return String(format: "$%.0fM", Double(amount) / 1_000_000) }
        return "$\(amount.formatted(.number.grouping(.automatic)))"
    }

    static func rating(_ value: Double) -> String { String(format: "★ %.1f", value) }
}
