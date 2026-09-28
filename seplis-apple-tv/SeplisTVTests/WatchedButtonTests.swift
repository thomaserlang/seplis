import XCTest
@testable import seplis_apple_tv

nonisolated final class WatchedButtonTests: XCTestCase {
    @MainActor func testInProgressLabelsDescribeResetEvenDuringRewatch() {
        for times in [0, 1, 3] {
            let button = WatchedButton(watched: Watched(times: times, position: 120), durationMinutes: 40,
                                       increment: {}, decrement: {})
            XCTAssertEqual(button.incrementTitle, "Mark as watched")
            XCTAssertEqual(button.decrementTitle, "Reset watched position")
        }
    }

    @MainActor func testCompletedWatchLabelsDescribeHistoryChanges() {
        for times in [1, 3] {
            let button = WatchedButton(watched: Watched(times: times, position: 0), durationMinutes: 40,
                                       increment: {}, decrement: {})
            XCTAssertEqual(button.incrementTitle, "Add another watch")
            XCTAssertEqual(button.decrementTitle, "Remove last watch")
        }
    }

    @MainActor func testProgressUsesRuntimeAndKeepsPartialWatchesVisible() {
        let quarter = WatchedButton(watched: Watched(times: 0, position: 600), durationMinutes: 40,
                                    increment: {}, decrement: {})
        XCTAssertEqual(quarter.progress, 0.25, accuracy: 0.001)

        let justStarted = WatchedButton(watched: Watched(times: 0, position: 10), durationMinutes: 40,
                                        increment: {}, decrement: {})
        XCTAssertEqual(justStarted.progress, 0.15, accuracy: 0.001)

        let noRuntime = WatchedButton(watched: Watched(times: 0, position: 120), durationMinutes: nil,
                                      increment: {}, decrement: {})
        XCTAssertEqual(noRuntime.progress, 0.5, accuracy: 0.001)
    }
}
