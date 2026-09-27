#if DEBUG
import Foundation
import Synchronization

enum UITestFixtures {
    static func session() -> AppSession {
        let configuration = URLSessionConfiguration.ephemeral
        configuration.protocolClasses = [FixtureURLProtocol.self]
        let transport = URLSession(configuration: configuration)
        let store = FixtureProfileStore()
        return AppSession(store: store, authorizationAPI: APIClient(session: transport),
                          makeClient: { APIClient(token: $0, session: transport) })
    }
}

private final class FixtureProfileStore: ProfileStore {
    var snapshot: ProfileSnapshot
    init() {
        snapshot = ProcessInfo.processInfo.arguments.contains("--login") ? ProfileSnapshot() : ProfileSnapshot(
            profiles: [.init(user: CurrentUser(id: 1, username: "Alex"), token: "fixture-one"),
                       .init(user: CurrentUser(id: 2, username: "Sam"), token: "fixture-two")], activeUserID: 1)
    }
    func load() throws -> ProfileSnapshot { snapshot }
    func save(_ snapshot: ProfileSnapshot) throws { self.snapshot = snapshot }
}

private nonisolated final class FixtureURLProtocol: URLProtocol, @unchecked Sendable {
    private static let loadedURLs = Mutex<Set<URL>>([])
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        if ProcessInfo.processInfo.arguments.contains("--loading-library") { return }
        if ProcessInfo.processInfo.arguments.contains("--fail-repeated-library-loads"),
           let url = request.url, ["/2/movies", "/2/series", "/2/users/me/watched"].contains(url.path),
           !Self.loadedURLs.withLock({ $0.insert(url).inserted }) {
            client?.urlProtocol(self, didFailWithError: URLError(.cannotConnectToHost))
            return
        }
        do {
            let object = FixtureResponses.response(for: request)
            let data = try JSONSerialization.data(withJSONObject: object, options: .fragmentsAllowed)
            let response = HTTPURLResponse(url: request.url!, statusCode: 200, httpVersion: nil, headerFields: nil)!
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch { client?.urlProtocol(self, didFailWithError: error) }
    }
    override func stopLoading() {}
}

private nonisolated enum FixtureResponses {
    static let watchedLoads = Mutex(0)
    static let movieWatchCount = Mutex(1)
    static let episodeWatchCounts = Mutex([1: 1, 2: 0])
    static var movie: [String: Any] {
        ["id": 1, "title": "National Treasure", "plot": "A historian follows clues to a hidden treasure.",
         "release_date": "2004-11-19", "runtime": 131, "genres": [["name": "Adventure"]],
         "poster_image": ["url": "https://images.seplis.net/2e32c887c4d6df85dd19100c82aac12b384bd640541f61ea3064fd30fe2ba7b7"],
         "user_watched": ["times": movieWatchCount.withLock { $0 }, "position": 0], "user_watchlist": ["on_watchlist": true],
         "user_favorite": ["favorite": false],
         "collection": ProcessInfo.processInfo.arguments.contains("--collections")
            ? ["id": 7, "name": "National Treasure Collection"] : NSNull()]
    }
    static var series: [String: Any] {
        ["id": 1, "title": "NCIS", "plot": "Special agents investigate crimes connected to the Navy.",
         "premiered": "2003-09-23", "seasons": [["season": 1, "total": 2]],
         "poster_image": ["url": "https://images.seplis.net/d30b15fd-4e0f-41cc-80cb-fb37079a2f5f"],
         "user_watchlist": ["on_watchlist": false], "user_favorite": ["favorite": true]]
    }
    static func episode(_ number: Int) -> [String: Any] {
        ["number": number, "season": 1, "episode": number, "title": number == 1 ? "Yankee White" : "Hung Out to Dry",
         "air_date": number == 1 ? "2003-09-23" : "2003-09-30",
         "user_watched": ["times": episodeWatchCounts.withLock { $0[number] ?? 0 }, "position": 0],
         "user_can_watch": ["on_play_server": number != 2 || !ProcessInfo.processInfo.arguments.contains("--unavailable-next-episode")]]
    }
    static func response(for request: URLRequest) -> Any {
        let path = request.url!.path
        func page(_ records: [Any]) -> [String: Any] {
            ["records": ProcessInfo.processInfo.arguments.contains("--empty-library") ? [] : records,
             "cursor": NSNull()]
        }
        if path == "/2/device-authorization" {
            return ["device_code": "fixture-device-secret", "user_code": "123456", "verification_uri": "https://seplis.net/device",
                    "verification_uri_complete": "https://seplis.net/device?code=123456",
                    "expires_at": "2099-01-01T00:00:00Z", "poll_interval_seconds": 3] as [String: Any]
        }
        if path.hasSuffix("/device-authorization/token") { return ["status": "pending"] }
        if path == "/2/users/me" { return ["id": 1, "username": "Alex"] as [String: Any] }
        if path == "/2/genres" { return [["id": 1, "name": "Adventure"], ["id": 2, "name": "Drama"]] }
        if path == "/2/search" {
            return [movie.merging(["type": "movie"]) { _, value in value },
                    series.merging(["type": "series"]) { _, value in value }]
        }
        if path == "/2/movies/1/watched" {
            let count = movieWatchCount.withLock { value in
                if request.httpMethod == "POST" { value += 1 }
                if request.httpMethod == "DELETE" { value = max(0, value - 1) }
                return value
            }
            return ["times": count, "position": 0]
        }
        if path == "/2/users/me/watched" {
            if ProcessInfo.processInfo.arguments.contains("--refresh-home") {
                let count = watchedLoads.withLock { $0 += 1; return $0 }
                let updated = movie.merging(["title": "Home refresh \(count)"]) { _, value in value }
                return page([["type": "movie", "data": updated]])
            }
            if ProcessInfo.processInfo.arguments.contains("--paginated-library") {
                let more = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)?.queryItems?
                    .contains { $0.name == "cursor" } == true
                let records = (more ? 25...48 : 1...24).map { id in
                    ["type": "movie", "data": movie.merging(["id": id]) { _, value in value }] as [String: Any]
                }
                return ["records": records, "cursor": more ? NSNull() : "next"] as [String: Any]
            }
            return page([["type": "movie", "data": movie], ["type": "series", "data": series]])
        }
        if path == "/2/movies" {
            if URLComponents(url: request.url!, resolvingAgainstBaseURL: false)?.queryItems?
                .contains(where: { $0.name == "collection_id" }) == true {
                return page([movie, sequel])
            }
            if ProcessInfo.processInfo.arguments.contains("--dense-catalog") {
                return page((1...36).map { id in movie.merging(["id": id]) { _, value in value } })
            }
            return page([movie])
        }
        if path == "/2/series" { return page([series]) }
        if path.hasSuffix("/to-watch") || path.hasSuffix("/recently-aired") {
            return page([["series": series, "episode": episode(2)]])
        }
        if path.hasSuffix("/episode-to-watch") { return episode(2) }
        if path.hasSuffix("/episode-last-watched") {
            return ProcessInfo.processInfo.arguments.contains("--single-episode-action") ? NSNull() : episode(1)
        }
        if path.hasSuffix("/episodes") { return page([episode(1), episode(2)]) }
        if path.hasPrefix("/2/movies/"), path.hasSuffix("/play-servers"),
           !ProcessInfo.processInfo.arguments.contains("--unavailable-movie") {
            return [["play_id": "fixture", "play_url": "https://play.example.test"]]
        }
        if path.hasSuffix("/play-servers") { return [] as [Any] }
        if path.hasPrefix("/2/series/1/episodes/"), path.hasSuffix("/watched") {
            let number = Int(request.url!.deletingLastPathComponent().lastPathComponent)!
            let count = episodeWatchCounts.withLock { counts in
                let change = request.httpMethod == "POST" ? 1 : request.httpMethod == "DELETE" ? -1 : 0
                counts[number] = max(0, (counts[number] ?? 0) + change)
                return counts[number]!
            }
            return ["times": count, "position": 0]
        }
        if path.hasSuffix("/watched") { return ["times": 1, "position": 0] }
        if path.contains("/episodes/") { return episode(Int(path.components(separatedBy: "/").last ?? "1") ?? 1) }
        if path == "/2/series/1" { return series }
        if path == "/2/movies/2" { return sequel }
        return movie
    }

    static var sequel: [String: Any] {
        movie.merging(["id": 2, "title": "National Treasure: Book of Secrets", "release_date": "2007-12-21"]) { _, value in value }
    }
}
#endif
