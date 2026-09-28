import XCTest

nonisolated final class MovieUITests: UITestCase {
    @MainActor func testMovieDetailsFromHome() {
        let app = launchApp()
        let movie = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "National Treasure")).firstMatch
        XCTAssertTrue(movie.waitForExistence(timeout: 10))
        let heading = app.staticTexts["Watched"].firstMatch
        XCTAssertLessThanOrEqual(movie.frame.minY - heading.frame.maxY, 12)
        XCTAssertLessThanOrEqual(movie.frame.minX, 40)
        select(movie, in: app)
        XCTAssertTrue(app.buttons["Play"].waitForExistence(timeout: 10))
        XCTAssertLessThan(abs(app.buttons["Play"].frame.midY - app.buttons["Watchlist"].frame.midY), 12)
        XCTAssertTrue(app.staticTexts["2h 11m"].exists)
        XCTAssertTrue(app.staticTexts["$100M"].exists)
        XCTAssertTrue(app.staticTexts["$348M"].exists)
        XCTAssertFalse(app.buttons["Start Over"].exists)
        XCTAssertEqual(app.buttons["Watchlist"].value as? String, "On")
        XCTAssertEqual(app.buttons["Favorite"].value as? String, "Off")
        attachScreenshot("Movie detail")
    }

    @MainActor func testCastFocusEntersFirstPortraitAndReturnsToActions() {
        let app = launchApp()
        let poster = app.buttons["media-movie-1"].firstMatch
        XCTAssertTrue(poster.waitForExistence(timeout: 10))
        select(poster, in: app)
        let favorite = app.buttons["Favorite"]
        XCTAssertTrue(favorite.waitForExistence(timeout: 5))
        for _ in 0..<5 where !favorite.hasFocus {
            XCUIRemote.shared.press(.right)
        }
        XCTAssertTrue(favorite.hasFocus)
        XCUIRemote.shared.press(.down)
        let firstCast = app.descendants(matching: .any)["cast-person-1"]
        XCTAssertTrue(firstCast.waitForExistence(timeout: 5))
        XCTAssertTrue(firstCast.hasFocus)
        XCUIRemote.shared.press(.up)
        XCTAssertTrue(["Play", "Watched", "Watchlist", "Favorite"].contains { app.buttons[$0].hasFocus })
    }

    @MainActor func testAvailableMovieCanPlay() {
        let app = launchApp()
        let poster = app.buttons["media-movie-1"].firstMatch
        XCTAssertTrue(poster.waitForExistence(timeout: 10))
        select(poster, in: app)
        let play = app.buttons["Play"]
        XCTAssertTrue(play.waitForExistence(timeout: 5))
        XCTAssertTrue(play.isEnabled)
    }

    @MainActor func testUnavailableMovieCannotPlay() {
        let app = launchApp(["--unavailable-movie"])
        let poster = app.buttons["media-movie-1"].firstMatch
        XCTAssertTrue(poster.waitForExistence(timeout: 10))
        select(poster, in: app)
        let play = app.buttons["Play"]
        XCTAssertTrue(play.waitForExistence(timeout: 5))
        XCTAssertFalse(play.isEnabled)
        XCTAssertTrue(app.buttons["Watchlist"].isEnabled)
        attachScreenshot("Unavailable movie")
    }

    @MainActor func testCollectionBackRestoresParentMovieAndCatalog() {
        let app = launchApp(["--collections"])
        XCTAssertTrue(app.buttons["Movies"].waitForExistence(timeout: 10))
        select(app.buttons["Movies"], in: app)
        let poster = app.buttons["grid-movie-1"]
        XCTAssertTrue(poster.waitForExistence(timeout: 5))
        select(poster, in: app)
        let sequel = app.buttons["collection-movie-2"]
        XCTAssertTrue(sequel.waitForExistence(timeout: 5))
        attachScreenshot("Movie collection")
        select(sequel, in: app)
        XCTAssertTrue(app.staticTexts["National Treasure: Book of Secrets"].waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(app.staticTexts["National Treasure"].waitForExistence(timeout: 5))
        XCTAssertTrue(sequel.hasFocus)
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(poster.waitForExistence(timeout: 5))
        XCTAssertTrue(poster.hasFocus)
    }

    @MainActor func testWatchedCounterMenu() {
        let app = launchApp()
        let poster = app.buttons["media-movie-1"].firstMatch
        XCTAssertTrue(poster.waitForExistence(timeout: 10))
        select(poster, in: app)
        let watched = app.buttons["Watched"]
        XCTAssertTrue(watched.waitForExistence(timeout: 5))
        XCTAssertEqual(watched.value as? String, "1 times")
        select(watched, in: app)
        XCTAssertTrue(app.buttons["Add another watch"].waitForExistence(timeout: 5))
        attachScreenshot("Watched counter menu")
        select(app.buttons["Add another watch"].firstMatch, in: app)
        let updated = XCTNSPredicateExpectation(predicate: NSPredicate(format: "value == %@", "2 times"), object: watched)
        XCTAssertEqual(XCTWaiter.wait(for: [updated], timeout: 5), .completed)
    }
}
