import XCTest
@testable import seplis_apple_tv

nonisolated final class TopShelfTests: XCTestCase {
    private let entry = TopShelfEntry(mediaID: 42, kind: "series", title: "Series - S1 E2",
                                     imageURL: URL(string: "https://example.com/poster.webp")!,
                                     episodeNumber: 2, progress: 0.25)

    func testLinksRoundTripAndRejectInvalidTargets() {
        for play in [true, false] {
            let link = TopShelfLink(accountID: 7, entry: entry, play: play)
            XCTAssertEqual(TopShelfLink(url: link.url), link)
        }
        for url in [
            "https://top-shelf/series/42?account=7&action=play&episode=2",
            "seplis://other/series/42?account=7&action=play&episode=2",
            "seplis://top-shelf/series/42?account=7&action=play",
            "seplis://top-shelf/series/42?account=7&action=play&episode=-1",
            "seplis://top-shelf/movie/-1?account=7&action=play",
            "seplis://top-shelf/movie/42?action=play",
        ] {
            XCTAssertNil(TopShelfLink(url: URL(string: url)!), url)
        }
    }

    func testSnapshotRoundTripAndClear() throws {
        let directory = try temporaryDirectory()
        defer { try? FileManager.default.removeItem(at: directory) }
        let store = TopShelfStore(directory: directory)
        XCTAssertNil(store.load())
        try store.save(TopShelfSnapshot(accountID: 7, items: [entry]))
        XCTAssertEqual(store.load()?.accountID, 7)
        XCTAssertEqual(store.load()?.items.first?.episodeNumber, 2)
        XCTAssertEqual(store.load()?.items.first?.progress, 0.25)
        try store.save(nil)
        XCTAssertNil(store.load())
    }

    @MainActor func testProfileChangeClearsSnapshotBeforeLoadingAndSignOutCancelsRefresh() async throws {
        let directory = try temporaryDirectory()
        defer { try? FileManager.default.removeItem(at: directory) }
        let store = TopShelfStore(directory: directory)
        try store.save(TopShelfSnapshot(accountID: 7, items: [entry]))
        let api = APIClient(session: stubSession { _ in
            XCTFail("Cancelled profile refresh must not make requests")
            return (200, Data(#"{"records":[]}"#.utf8))
        })
        api.accountID = 8
        let publisher = TopShelfPublisher(store: store, contentDidChange: {})
        publisher.configure(api: api)
        XCTAssertNil(store.load())
        publisher.configure(api: nil)
        await publisher.refreshTask?.value
        XCTAssertNil(store.load())
    }

    @MainActor func testPublisherUsesNextEpisodeAndOnlyUnfinishedAvailableMovies() async throws {
        let directory = try temporaryDirectory()
        defer { try? FileManager.default.removeItem(at: directory) }
        let store = TopShelfStore(directory: directory)
        let api = APIClient(session: stubSession { request in
            let response: String
            switch request.url!.path {
            case "/2/users/me/watched":
                XCTAssertTrue(request.url!.query!.contains("user_can_watch=true"))
                response = #"{"records":[{"type":"series","data":{"id":1,"title":"Series","poster_image":{"url":"https://example.com/1"}}},{"type":"movie","data":{"id":2,"title":"Movie","runtime":100,"poster_image":{"url":"https://example.com/2"}}},{"type":"movie","data":{"id":3,"poster_image":{"url":"https://example.com/3"}}},{"type":"series","data":{"id":4,"poster_image":{"url":"https://example.com/4"}}}]}"#
            case "/2/series/1/episode-to-watch":
                response = #"{"number":12,"season":2,"episode":2,"runtime":40,"user_watched":{"times":0,"position":600},"user_can_watch":{"on_play_server":true}}"#
            case "/2/movies/2/watched":
                response = #"{"times":1,"position":3000}"#
            case "/2/movies/3/watched":
                response = #"{"times":1,"position":0}"#
            case "/2/series/4/episode-to-watch":
                response = #"{"number":9,"user_can_watch":{"on_play_server":false}}"#
            default:
                XCTFail("Unexpected request: \(request.url!)")
                return (404, Data())
            }
            return (200, Data(response.utf8))
        })
        api.accountID = 7
        let publisher = TopShelfPublisher(store: store, contentDidChange: {})
        publisher.configure(api: api)
        await publisher.refreshTask?.value
        let snapshot = try XCTUnwrap(store.load())
        XCTAssertEqual(snapshot.accountID, 7)
        XCTAssertEqual(snapshot.items.map(\.mediaID), [1, 2])
        XCTAssertEqual(snapshot.items[0].episodeNumber, 12)
        XCTAssertEqual(snapshot.items[0].progress, 0.25)
        XCTAssertEqual(snapshot.items[1].progress, 0.5)
        XCTAssertNil(snapshot.items[1].episodeNumber)
    }

    private func temporaryDirectory() throws -> URL {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
        return url
    }
}
