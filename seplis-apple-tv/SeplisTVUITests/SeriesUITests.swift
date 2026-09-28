import XCTest

nonisolated final class SeriesUITests: UITestCase {
    @MainActor func testSeriesDetailsAndSeasonPlayback() {
        let app = launchApp()
        let series = app.buttons["media-series-1"].firstMatch
        XCTAssertTrue(series.waitForExistence(timeout: 10))
        select(series, in: app)
        let nextPlay = app.buttons.matching(NSPredicate(format: "label BEGINSWITH %@", "Play S1 E2")).firstMatch
        let nextPlayFocused = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: nextPlay)
        XCTAssertEqual(XCTWaiter.wait(for: [nextPlayFocused], timeout: 5), .completed)
        XCTAssertLessThan(app.buttons["Watchlist"].frame.maxY, nextPlay.frame.minY)
        XCTAssertTrue(app.staticTexts["43 min"].exists)
        XCTAssertTrue(app.staticTexts["2"].exists)
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

    @MainActor func testRepeatedSeriesPresentationMovesFocusIntoDetailsAndBack() {
        let app = launchApp()
        let poster = app.buttons["media-series-1"].firstMatch
        XCTAssertTrue(poster.waitForExistence(timeout: 10))
        for _ in 0..<3 {
            select(poster, in: app)
            let play = app.buttons["Play S1 E2"]
            XCTAssertTrue(play.waitForExistence(timeout: 5))
            let focused = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: play)
            XCTAssertEqual(XCTWaiter.wait(for: [focused], timeout: 5), .completed)
            XCUIRemote.shared.press(.right)
            XCTAssertTrue(app.buttons["episode-watched-2"].hasFocus)
            XCUIRemote.shared.press(.menu)
            let restored = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: poster)
            XCTAssertEqual(XCTWaiter.wait(for: [restored], timeout: 5), .completed)
        }
    }

    @MainActor func testUnavailableNextEpisodeFocusesRewatchAndShowsAirDates() {
        let app = launchApp(["--unavailable-next-episode"])
        let poster = app.buttons["media-series-1"].firstMatch
        XCTAssertTrue(poster.waitForExistence(timeout: 10))
        select(poster, in: app)
        let rewatch = app.buttons["Rewatch S1 E1"]
        XCTAssertTrue(rewatch.waitForExistence(timeout: 5))
        XCTAssertTrue(rewatch.hasFocus)
        XCTAssertFalse(app.buttons["Play S1 E2"].isEnabled)
        XCTAssertTrue(app.staticTexts["Next to watch"].exists)
        XCTAssertTrue(app.staticTexts["2003-09-30"].exists)
        let season = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "Season 1")).firstMatch
        select(season, in: app)
        XCTAssertTrue(app.staticTexts["2003-09-23"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["2003-09-30"].exists)
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(rewatch.waitForExistence(timeout: 5))
    }

    @MainActor func testSingleEpisodeCardWidth() {
        let app = launchApp(["--single-episode-action"])
        XCTAssertTrue(app.buttons["Series"].waitForExistence(timeout: 10))
        select(app.buttons["Series"], in: app)
        select(app.buttons["grid-series-1"], in: app)
        let card = app.otherElements["episode-actions-2"]
        XCTAssertTrue(card.waitForExistence(timeout: 5))
        XCTAssertGreaterThan(card.frame.width, 300)
        XCTAssertLessThan(card.frame.width, app.frame.width * 0.55)
        XCTAssertFalse(app.staticTexts["Last watched"].exists)
        XCTAssertTrue(app.buttons["episode-watched-2"].exists)
        attachScreenshot("Single episode card")
    }

    @MainActor func testEpisodeWatchedCountersInDetailsAndSeason() {
        let app = launchApp()
        let poster = app.buttons["media-series-1"].firstMatch
        XCTAssertTrue(poster.waitForExistence(timeout: 10))
        select(poster, in: app)
        let watched = app.buttons["episode-watched-2"]
        XCTAssertTrue(watched.waitForExistence(timeout: 5))
        select(watched, in: app)
        let incremented = XCTNSPredicateExpectation(predicate: NSPredicate(format: "value == %@", "1 times"), object: watched)
        XCTAssertEqual(XCTWaiter.wait(for: [incremented], timeout: 5), .completed)
        XCTAssertEqual(app.buttons["episode-watched-1"].value as? String, "1 times")
        attachScreenshot("Episode actions with watched counters")
        let season = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "Season 1")).firstMatch
        select(season, in: app)
        XCTAssertTrue(watched.waitForExistence(timeout: 5))
        XCTAssertEqual(watched.value as? String, "1 times")
        select(watched, in: app)
        select(app.buttons["Remove last watch"].firstMatch, in: app)
        let decremented = XCTNSPredicateExpectation(predicate: NSPredicate(format: "value == %@", "0 times"), object: watched)
        XCTAssertEqual(XCTWaiter.wait(for: [decremented], timeout: 5), .completed)
        attachScreenshot("Season watched counters")
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(season.waitForExistence(timeout: 5))
        XCTAssertEqual(watched.value as? String, "0 times")
    }

    @MainActor func testBackReturnsThroughSeasonAndRestoresCatalogPoster() {
        let app = launchApp()
        XCTAssertTrue(app.buttons["Series"].waitForExistence(timeout: 10))
        select(app.buttons["Series"], in: app)
        let poster = app.buttons["grid-series-1"]
        XCTAssertTrue(poster.waitForExistence(timeout: 5))
        select(poster, in: app)
        let season = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "Season 1")).firstMatch
        XCTAssertTrue(season.waitForExistence(timeout: 5))
        select(season, in: app)
        XCTAssertTrue(app.buttons.matching(NSPredicate(format: "label CONTAINS %@", "Hung Out to Dry")).firstMatch.waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(season.waitForExistence(timeout: 5))
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(poster.waitForExistence(timeout: 5))
        let focused = XCTNSPredicateExpectation(predicate: NSPredicate(format: "hasFocus == true"), object: poster)
        XCTAssertEqual(XCTWaiter.wait(for: [focused], timeout: 5), .completed)
        XCTAssertFalse(app.staticTexts["Watched"].isHittable)
    }
}
