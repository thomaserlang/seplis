import XCTest

nonisolated final class HomeUITests: UITestCase {
    @MainActor func testHomeRefreshesOnTabReturnAndDetailDismissal() {
        let app = launchApp(["--refresh-home"])
        XCTAssertTrue(app.buttons["Home refresh 1"].waitForExistence(timeout: 10))
        XCUIRemote.shared.press(.up)
        XCUIRemote.shared.press(.right)
        XCTAssertTrue(app.buttons["series-filters"].waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.left)
        XCTAssertTrue(app.buttons["Home refresh 2"].waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.down)
        XCTAssertTrue(app.buttons["Home refresh 2"].hasFocus)
        XCUIRemote.shared.press(.select)
        XCTAssertTrue(app.buttons["Play"].waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(app.buttons["Home refresh 3"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["Home refresh 3"].hasFocus)
    }

    @MainActor func testShelfAutomaticallyLoadsNextPage() {
        let app = launchApp(["--paginated-library"])
        let first = app.buttons["media-movie-1"].firstMatch
        XCTAssertTrue(first.waitForExistence(timeout: 10))
        let focused = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: first)
        XCTAssertEqual(XCTWaiter.wait(for: [focused], timeout: 5), .completed)
        for _ in 0..<25 { XCUIRemote.shared.press(.right) }
        let nextPagePoster = app.buttons["media-movie-26"]
        XCTAssertTrue(nextPagePoster.waitForExistence(timeout: 5))
        XCTAssertTrue(nextPagePoster.hasFocus)
        XCTAssertFalse(app.buttons["More"].exists)
        attachScreenshot("Continuous shelf across page boundary")
        XCUIRemote.shared.press(.select)
        XCTAssertTrue(app.buttons["Play"].waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(nextPagePoster.waitForExistence(timeout: 5))
        let restored = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: nextPagePoster)
        XCTAssertEqual(XCTWaiter.wait(for: [restored], timeout: 5), .completed)
        XCUIRemote.shared.press(.up)
        XCTAssertTrue(app.buttons["Home"].hasFocus)
        XCUIRemote.shared.press(.down)
        let firstRestored = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: first)
        XCTAssertEqual(XCTWaiter.wait(for: [firstRestored], timeout: 5), .completed)
    }

    @MainActor func testEmptyShelvesAreHidden() {
        let app = launchApp(["--empty-library"])
        XCTAssertTrue(app.buttons["Home"].waitForExistence(timeout: 10))
        XCTAssertFalse(app.buttons["Refresh"].exists)
        XCTAssertFalse(app.staticTexts["Watched"].exists)
        XCTAssertFalse(app.staticTexts["Movie watchlist"].exists)
        XCTAssertFalse(app.staticTexts["No titles available"].exists)
    }

    @MainActor func testLoadingShelvesReservePosterHeight() {
        let app = launchApp(["--loading-library"])
        let first = app.staticTexts["Watched"]
        let second = app.staticTexts["Series to Watch"]
        XCTAssertTrue(second.waitForExistence(timeout: 10))
        XCTAssertGreaterThan(second.frame.minY - first.frame.minY, 290)
        XCTAssertLessThan(second.frame.minY - first.frame.minY, 340)
        XCTAssertFalse(app.buttons["media-movie-1"].exists)
        XCTAssertFalse(app.buttons["Add Account"].exists)
        attachScreenshot("Poster loading skeletons")
    }

    @MainActor func testInitialPosterFocusAndCompactNavigation() {
        let app = launchApp()
        let first = app.buttons["media-movie-1"].firstMatch
        XCTAssertTrue(first.waitForExistence(timeout: 10))
        let focused = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: first)
        XCTAssertEqual(XCTWaiter.wait(for: [focused], timeout: 5), .completed)
        XCTAssertLessThan(app.staticTexts["Watched"].firstMatch.frame.minY, 120)
        XCTAssertLessThan(app.buttons["Search"].frame.maxX, app.buttons["Home"].frame.minX)
        attachScreenshot("Compact home with poster focus")
        XCUIRemote.shared.press(.up)
        XCTAssertTrue(app.buttons["Home"].hasFocus)
        attachScreenshot("Compact navigation focus")
    }
}
