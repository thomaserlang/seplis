import XCTest

nonisolated final class ProfileUITests: UITestCase {
    @MainActor func testProfileMenuReturnsFocusAndAddsAccount() {
        let app = launchApp()
        XCTAssertTrue(app.staticTexts["Watched"].waitForExistence(timeout: 15))
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

    @MainActor func testSwitchProfileAndRemoveAccountNavigation() {
        let app = launchApp()
        let profiles = app.descendants(matching: .any)["profiles-menu"]
        XCTAssertTrue(profiles.waitForExistence(timeout: 10))
        openProfiles(in: app)
        select(app.buttons["Remove an Account"], in: app)
        XCTAssertTrue(app.buttons["Back"].exists)
        XCUIRemote.shared.press(.menu)
        XCTAssertTrue(app.buttons["Add Account"].exists)
        XCTAssertTrue(app.buttons["Remove an Account"].hasFocus)
        let sam = menuItem("Sam", in: app)
        XCTAssertTrue(sam.waitForExistence(timeout: 5))
        select(sam, in: app)
        XCTAssertTrue(app.staticTexts["Watched"].waitForExistence(timeout: 10))
        openProfiles(in: app)
        XCTAssertTrue(menuItem("Sign Out of Sam", in: app).waitForExistence(timeout: 5))
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
