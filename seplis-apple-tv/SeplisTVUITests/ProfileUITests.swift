import XCTest

nonisolated final class ProfileUITests: UITestCase {
    @MainActor func testDeviceLoginScreen() {
        let app = launchApp(["--login"])
        XCTAssertTrue(app.staticTexts["seplis.net/device"].waitForExistence(timeout: 10))
        XCTAssertTrue(app.images["SEPLIS"].exists)
        XCTAssertTrue(app.staticTexts["Then enter this code"].exists)
        XCTAssertTrue(app.staticTexts["Sign-in code 123456"].exists)
        attachScreenshot("Device login")
    }

    @MainActor func testHomeDetailAndProfiles() {
        let app = launchApp()
        XCTAssertTrue(app.staticTexts["Watched"].waitForExistence(timeout: 15))
        attachScreenshot("Home")
        let movie = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "National Treasure")).firstMatch
        XCTAssertTrue(movie.waitForExistence(timeout: 10))
        let heading = app.staticTexts["Watched"].firstMatch
        XCTAssertLessThanOrEqual(movie.frame.minY - heading.frame.maxY, 12)
        XCTAssertLessThanOrEqual(movie.frame.minX, 40)
        select(movie, in: app)
        XCTAssertTrue(app.buttons["Play"].waitForExistence(timeout: 10))
        XCTAssertFalse(app.buttons["Start Over"].exists)
        XCTAssertEqual(app.buttons["Watchlist"].value as? String, "On")
        XCTAssertEqual(app.buttons["Favorite"].value as? String, "Off")
        attachScreenshot("Movie detail")
        XCUIRemote.shared.press(.menu)
        let profiles = app.buttons["Profiles"]
        XCTAssertTrue(profiles.waitForExistence(timeout: 5))
        select(profiles, in: app)
        XCTAssertTrue(app.buttons["Add Account"].waitForExistence(timeout: 5))
        attachScreenshot("Profiles")
        select(app.buttons["Add Account"], in: app)
        XCTAssertTrue(app.staticTexts["seplis.net/device"].waitForExistence(timeout: 10))
        attachScreenshot("Add account")
    }

    @MainActor func testSwitchProfileAndBrowseSeason() {
        let app = launchApp()
        XCTAssertTrue(app.buttons["Profiles"].waitForExistence(timeout: 10))
        select(app.buttons["Profiles"], in: app)
        let sam = app.buttons["profile-2"]
        XCTAssertTrue(sam.waitForExistence(timeout: 5))
        select(sam, in: app)
        XCTAssertTrue(app.staticTexts["Watched"].waitForExistence(timeout: 10))
        select(app.buttons["Profiles"], in: app)
        XCTAssertTrue(app.buttons["Sign Out of Sam"].waitForExistence(timeout: 5))
        select(app.buttons["Home"], in: app)
        let series = app.buttons["media-series-1"].firstMatch
        XCTAssertTrue(series.waitForExistence(timeout: 5))
        select(series, in: app)
        let season = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "Season 1")).firstMatch
        XCTAssertTrue(season.waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["episode-watched-2"].exists)
        attachScreenshot("Series detail")
        select(season, in: app)
        let episode = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "Hung Out to Dry")).firstMatch
        XCTAssertTrue(episode.waitForExistence(timeout: 5))
        attachScreenshot("Season")
        select(episode, in: app)
        XCTAssertTrue(app.staticTexts["No play server has this title available for your account."].waitForExistence(timeout: 10))
        attachScreenshot("Episode playback")
    }
}
