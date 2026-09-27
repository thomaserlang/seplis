import Foundation

nonisolated struct TopShelfLink: Identifiable, Equatable {
    let accountID: Int
    let kind: String
    let mediaID: Int
    let episodeNumber: Int?
    let play: Bool

    var id: String { url.absoluteString }

    var url: URL {
        var parts = URLComponents()
        parts.scheme = "seplis"
        parts.host = "top-shelf"
        parts.path = "/\(kind)/\(mediaID)"
        parts.queryItems = [
            .init(name: "account", value: String(accountID)),
            .init(name: "action", value: play ? "play" : "details"),
        ]
        if let episodeNumber {
            parts.queryItems?.append(.init(name: "episode", value: String(episodeNumber)))
        }
        return parts.url!
    }

    init(accountID: Int, entry: TopShelfEntry, play: Bool) {
        self.accountID = accountID
        kind = entry.kind
        mediaID = entry.mediaID
        episodeNumber = entry.episodeNumber
        self.play = play
    }

    init?(url: URL) {
        guard let parts = URLComponents(url: url, resolvingAgainstBaseURL: false),
              parts.scheme == "seplis", parts.host == "top-shelf" else { return nil }
        let path = parts.path.split(separator: "/")
        let query = parts.queryItems ?? []
        guard path.count == 2, ["series", "movie"].contains(String(path[0])),
              let mediaID = Int(path[1]), mediaID > 0,
              let account = query.first(where: { $0.name == "account" })?.value,
              let accountID = Int(account), accountID > 0,
              let action = query.first(where: { $0.name == "action" })?.value,
              ["play", "details"].contains(action) else { return nil }
        let episode = query.first(where: { $0.name == "episode" })?.value
        if let episode, Int(episode).map({ $0 > 0 }) != true { return nil }
        self.accountID = accountID
        self.mediaID = mediaID
        kind = String(path[0])
        episodeNumber = episode.flatMap(Int.init)
        play = action == "play"
        if kind == "series", play, episodeNumber == nil { return nil }
    }
}
