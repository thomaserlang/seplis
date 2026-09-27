import XCTest
@testable import seplis_apple_tv

nonisolated final class WatchedButtonTests: XCTestCase {
    @MainActor func testInProgressLabelsDescribeResetEvenDuringRewatch() {
        for times in [0, 1, 3] {
            let button = WatchedButton(watched: Watched(times: times, position: 120), increment: {}, decrement: {})
            XCTAssertEqual(button.incrementTitle, "Mark as watched")
            XCTAssertEqual(button.decrementTitle, "Reset watched position")
        }
    }

    @MainActor func testCompletedWatchLabelsDescribeHistoryChanges() {
        for times in [1, 3] {
            let button = WatchedButton(watched: Watched(times: times, position: 0), increment: {}, decrement: {})
            XCTAssertEqual(button.incrementTitle, "Add another watch")
            XCTAssertEqual(button.decrementTitle, "Remove last watch")
        }
    }
}
