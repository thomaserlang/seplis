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
    var originalURL: URL? { URL(string: url) }
}

nonisolated struct Genre: Decodable {
    let name: String
}
