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
        let profiles = app.descendants(matching: .any)["profiles-menu"]
        XCTAssertTrue(profiles.waitForExistence(timeout: 5))
        openProfiles(in: app)
        let addAccount = menuItem("Add Account", in: app)
        XCTAssertTrue(addAccount.waitForExistence(timeout: 5))
        attachScreenshot("Profiles menu")
        let activeTab = app.buttons[app.searchFields.firstMatch.exists ? "Search" : "Home"]
        XCUIRemote.shared.press(.menu)
        XCTAssertFalse(addAccount.exists)
        let restored = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: activeTab)
        XCTAssertEqual(XCTWaiter.wait(for: [restored], timeout: 5), .completed)
        openProfiles(in: app)
        select(addAccount, in: app)
        XCTAssertTrue(app.staticTexts["seplis.net/device"].waitForExistence(timeout: 10))
        attachScreenshot("Add account")
    }

    @MainActor func testSwitchProfileAndBrowseSeason() {
        let app = launchApp()
        let profiles = app.descendants(matching: .any)["profiles-menu"]
        XCTAssertTrue(profiles.waitForExistence(timeout: 10))
        openProfiles(in: app)
        select(app.buttons["Remove Account"], in: app)
        XCTAssertTrue(app.buttons["Back"].exists)
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(app.buttons["Add Account"].exists)
        XCTAssertTrue(app.buttons["Remove Account"].hasFocus)
        let sam = menuItem("Sam", in: app)
        XCTAssertTrue(sam.waitForExistence(timeout: 5))
        select(sam, in: app)
        XCTAssertTrue(app.staticTexts["Watched"].waitForExistence(timeout: 10))
        openProfiles(in: app)
        XCTAssertTrue(menuItem("Sign Out of Sam", in: app).waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.menu)
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

    @MainActor private func menuItem(_ title: String, in app: XCUIApplication) -> XCUIElement {
        app.buttons.matching(NSPredicate(format: "label BEGINSWITH %@", title)).firstMatch
    }

    @MainActor private func openProfiles(in app: XCUIApplication) {
        let profiles = app.buttons["profiles-menu"]
        let addAccount = menuItem("Add Account", in: app)
        if addAccount.exists { return }
        if profiles.hasFocus {
            XCUIRemote.shared.press(.select)
        } else {
            if !["Search", "Home", "Series", "Movies"].contains(where: { app.buttons[$0].hasFocus }) {
                XCUIRemote.shared.press(.menu)
            }
            for _ in 0..<5 {
                if addAccount.exists { break }
                XCUIRemote.shared.press(.left)
            }
        }
        XCTAssertTrue(addAccount.waitForExistence(timeout: 5))
    }
}
