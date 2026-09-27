import Foundation

nonisolated struct PlayMediaResponse: Decodable {
    let hlsUrl: String
    let keepAliveUrl: String
    let closeSessionUrl: String
    var transcodeDecision: TranscodeDecision? = nil

    func session(relativeTo base: URL) throws -> PlaySession {
        func resolve(_ value: String) throws -> URL {
            // Play-server paths are relative to its mount point, including leading-slash URLs.
            let url = value.hasPrefix("/")
                ? URL(string: base.absoluteString.trimmingCharacters(in: CharacterSet(charactersIn: "/")) + value)
                : URL(string: value, relativeTo: base.appending(path: ""))?.absoluteURL
            guard let url, ["http", "https"].contains(url.scheme), url.host != nil else {
                throw APIError.invalidResponse
            }
            return url
        }
        return try PlaySession(hlsURL: resolve(hlsUrl), keepAliveURL: resolve(keepAliveUrl),
                               closeURL: resolve(closeSessionUrl), decision: transcodeDecision)
    }
}

nonisolated struct PlaySession {
    let hlsURL: URL
    let keepAliveURL: URL
    let closeURL: URL
    var decision: TranscodeDecision? = nil
}
