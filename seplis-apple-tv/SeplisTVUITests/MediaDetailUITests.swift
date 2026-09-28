import XCTest

nonisolated final class MediaDetailUITests: UITestCase {
    @MainActor func testLoadingDetailsOwnFocusAndBackRestoresHomePoster() {
        let app = launchApp(["--loading-media-details"])
        let poster = app.buttons["media-series-1"].firstMatch
        XCTAssertTrue(poster.waitForExistence(timeout: 10))
        select(poster, in: app)
        let loading = app.descendants(matching: .any).matching(identifier: "media-detail-loading").firstMatch
        XCTAssertTrue(loading.waitForExistence(timeout: 5))
        let focused = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: loading)
        XCTAssertEqual(XCTWaiter.wait(for: [focused], timeout: 5), .completed)
        for direction in [XCUIRemote.Button.right, .down, .left, .up] {
            XCUIRemote.shared.press(direction)
            XCTAssertTrue(loading.hasFocus)
            XCTAssertFalse(poster.hasFocus)
        }
        XCUIRemote.shared.press(.menu)
        let restored = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: poster)
        XCTAssertEqual(XCTWaiter.wait(for: [restored], timeout: 5), .completed)
    }
}
