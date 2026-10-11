import Foundation

nonisolated struct MediaSummary: Decodable, Identifiable {
    let id: Int
    let title: String?
    let posterImage: Poster?
    let runtime: Int?

    var displayTitle: String { title ?? "Untitled" }
}
