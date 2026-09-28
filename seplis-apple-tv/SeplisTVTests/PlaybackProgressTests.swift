import Synchronization
import XCTest
@testable import seplis_apple_tv

nonisolated final class PlaybackProgressTests: XCTestCase {
    @MainActor func testEarlyExitDoesNotSaveProgress() async {
        let count = Mutex(0)
        let transport = stubSession { _ in count.withLock { $0 += 1 }; return (204, Data()) }
        let progress = PlaybackProgress(api: APIClient(session: transport), path: "series/1/episodes/2", start: 0)
        for position in [0.0, 1, 5, 9.99] {
            progress.record(position: position, duration: 2400)
        }
        await progress.flush()
        XCTAssertEqual(count.withLock { $0 }, 0)
    }

    @MainActor func testResumeWaitsForTenSecondsOfPositionChange() async {
        let count = Mutex(0)
        let transport = stubSession { _ in count.withLock { $0 += 1 }; return (204, Data()) }
        let progress = PlaybackProgress(api: APIClient(session: transport), path: "series/1/episodes/2", start: 120)
        progress.record(position: 120, duration: 2400)
        progress.record(position: 129.99, duration: 2400)
        await progress.flush()
        XCTAssertEqual(count.withLock { $0 }, 0)
        progress.record(position: 130, duration: 2400)
        await progress.flush()
        XCTAssertEqual(count.withLock { $0 }, 1)
        progress.record(position: 131, duration: 2400)
        await progress.flush()
        XCTAssertEqual(count.withLock { $0 }, 1)
    }

    @MainActor func testProgressIsOrderedAndCompletionHappensOnce() async {
        let paths = Mutex<[String]>([])
        let transport = stubSession { request in
            paths.withLock { $0.append("\(request.httpMethod!) \(request.url!.path)") }
            return (204, Data())
        }
        let progress = PlaybackProgress(api: APIClient(session: transport), path: "movies/42", start: 0)
        progress.record(position: 10, duration: 100)
        progress.record(position: 20, duration: 100)
        progress.record(position: 90, duration: 100)
        progress.record(position: 95, duration: 100)
        await progress.flush()
        XCTAssertEqual(paths.withLock { $0 }, ["PUT /2/movies/42/watched-position", "PUT /2/movies/42/watched-position", "POST /2/movies/42/watched"])
    }

    @MainActor func testInvalidDurationDoesNotMarkWatched() async {
        let count = Mutex(0)
        let transport = stubSession { _ in count.withLock { $0 += 1 }; return (204, Data()) }
        let progress = PlaybackProgress(api: APIClient(session: transport), path: "movies/42", start: 0)
        progress.record(position: 0, duration: 0)
        progress.record(position: 50, duration: .nan)
        await progress.flush()
        XCTAssertEqual(count.withLock { $0 }, 0)
        XCTAssertFalse(progress.completed)
    }

    @MainActor func testNaturalEndMarksWatchedWithoutDuration() async {
        let paths = Mutex<[String]>([])
        let transport = stubSession { request in
            paths.withLock { $0.append("\(request.httpMethod!) \(request.url!.path)") }
            return (204, Data())
        }
        let progress = PlaybackProgress(api: APIClient(session: transport), path: "movies/42", start: 0)
        progress.finish()
        progress.finish()
        await progress.flush()
        XCTAssertTrue(progress.completed)
        XCTAssertEqual(paths.withLock { $0 }, ["POST /2/movies/42/watched"])
    }

    @MainActor func testAmbiguousCompletionFailureIsNotRetried() async {
        let count = Mutex(0)
        let transport = stubSession { _ in count.withLock { $0 += 1 }; return (500, Data()) }
        let progress = PlaybackProgress(api: APIClient(session: transport), path: "movies/42", start: 0)
        progress.record(position: 90, duration: 100)
        await progress.flush()
        progress.record(position: 99, duration: 100)
        await progress.flush()
        XCTAssertEqual(count.withLock { $0 }, 1)
        XCTAssertNotNil(progress.error)
    }
}
