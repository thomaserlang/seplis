import Synchronization
import XCTest
@testable import seplis_apple_tv

nonisolated final class HomeShelfTests: XCTestCase {
    @MainActor func testRefreshRetainsLoadedPagesAndUsesFreshCursors() async {
        let cursors = Mutex<[String?]>([])
        let transport = stubSession { request in
            let cursor = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)!
                .queryItems!.first { $0.name == "cursor" }?.value
            let count = cursors.withLock { $0.append(cursor); return $0.count }
            let records = (cursor == nil ? 1...24 : 25...48)
                .map { "{\"id\":\($0)}" }.joined(separator: ",")
            let next = cursor == nil ? "\"page-two-\(count)\"" : "\"page-three\""
            return (200, Data("{\"records\":[\(records)],\"cursor\":\(next)}".utf8))
        }
        let model = HomeShelfModel(shelf: .popularMovies, api: APIClient(session: transport))
        await model.load()
        await model.load(more: true)
        let ids = model.items.map(\.id)
        await model.load()
        XCTAssertEqual(model.items.map(\.id), ids)
        XCTAssertEqual(model.items.count, 48)
        XCTAssertEqual(model.cursor, "page-three")
        XCTAssertEqual(cursors.withLock { $0 }, [nil, "page-two-1", nil, "page-two-3"])
    }

    @MainActor func testLaterPageRefreshFailureKeepsEntireLoadedShelf() async {
        let requests = Mutex(0)
        let transport = stubSession { request in
            let count = requests.withLock { $0 += 1; return $0 }
            if count == 4 { throw URLError(.cannotConnectToHost) }
            let more = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)!
                .queryItems!.contains { $0.name == "cursor" }
            let id = more ? 2 : (count == 3 ? 99 : 1)
            return (200, Data("{\"records\":[{\"id\":\(id)}],\"cursor\":\(more ? "null" : "\"next\"")}".utf8))
        }
        let model = HomeShelfModel(shelf: .popularMovies, api: APIClient(session: transport))
        await model.load()
        await model.load(more: true)
        await model.load()
        XCTAssertEqual(model.items.map(\.media.id), [1, 2])
        XCTAssertNil(model.cursor)
        XCTAssertNotNil(model.error)
        XCTAssertFalse(model.isLoading)
    }

    @MainActor func testHomeRefreshKeepsCachedCardsUntilResponseAndOnFailure() async throws {
        let requests = Mutex(0)
        let transport = stubSession { _ in
            let number = requests.withLock { $0 += 1; return $0 }
            if number == 3 { throw URLError(.cannotConnectToHost) }
            if number == 2 { Thread.sleep(forTimeInterval: 0.2) }
            return (200, Data("{\"records\":[{\"id\":\(number)}],\"cursor\":null}".utf8))
        }
        let model = HomeShelfModel(shelf: .popularMovies, api: APIClient(session: transport))
        await model.load()
        let refresh = Task { await model.load() }
        for _ in 0..<100 {
            if model.isLoading { break }
            try await Task.sleep(for: .milliseconds(1))
        }
        XCTAssertTrue(model.isLoading)
        XCTAssertFalse(model.isLoadingMore)
        XCTAssertEqual(model.items.map(\.media.id), [1])
        await refresh.value
        XCTAssertEqual(model.items.map(\.media.id), [2])
        await model.load()
        XCTAssertEqual(model.items.map(\.media.id), [2])
        XCTAssertNotNil(model.error)
    }

    @MainActor func testShelfPreloadsOnlyNearEndAndStopsAtLastPage() async {
        let requests = Mutex(0)
        let transport = stubSession { request in
            requests.withLock { $0 += 1 }
            let more = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)!.queryItems!.contains { $0.name == "cursor" }
            let records = (more ? 24...30 : 1...24).map { "{\"id\":\($0)}" }.joined(separator: ",")
            return (200, Data("{\"records\":[\(records)],\"cursor\":\(more ? "null" : "\"next\"")}".utf8))
        }
        let model = HomeShelfModel(shelf: .popularMovies, api: APIClient(session: transport))
        await model.load()
        await model.loadMoreIfNeeded(near: model.items[0].id)
        XCTAssertEqual(requests.withLock { $0 }, 1)
        await model.loadMoreIfNeeded(near: model.items[18].id)
        XCTAssertEqual(model.items.count, 30)
        XCTAssertEqual(requests.withLock { $0 }, 2)
        await model.loadMoreIfNeeded(near: model.items.last!.id)
        XCTAssertEqual(requests.withLock { $0 }, 2)
    }
}
