import XCTest

nonisolated final class PlaybackUITests: UITestCase {
    @MainActor func testNativeInfoMenusScrollAndGoBack() {
        let app = launchApp(["--playback-info-fixture"])
        let open = app.buttons["open-media-info"]
        XCTAssertTrue(open.waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.select)
        XCTAssertTrue(menuRow("Playback Decision", in: app).waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.select)
        XCTAssertTrue(menuRow("Delivery", in: app).waitForExistence(timeout: 5))
        attachScreenshot("Native playback decision")
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(menuRow("Media Info", in: app).waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.down)
        XCUIRemote.shared.press(.select)
        XCTAssertTrue(menuRow("Quality", in: app).waitForExistence(timeout: 5))
        for _ in 0..<14 { XCUIRemote.shared.press(.down) }
        let language = menuRow("Audio language", in: app)
        XCTAssertTrue(language.exists)
        XCTAssertLessThan(language.frame.maxY, app.frame.maxY)
        attachScreenshot("Native media info scrolled")
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(menuRow("Playback Decision", in: app).waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.menu)
        let visible = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hittable == true"), object: open)
        XCTAssertEqual(XCTWaiter.wait(for: [visible], timeout: 5), .completed)
    }

    @MainActor private func menuRow(_ title: String, in app: XCUIApplication) -> XCUIElement {
        app.otherElements.matching(NSPredicate(format: "label BEGINSWITH %@", title)).firstMatch
    }
}
