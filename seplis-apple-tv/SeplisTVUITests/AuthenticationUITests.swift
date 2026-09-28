import XCTest

nonisolated final class AuthenticationUITests: UITestCase {
    @MainActor func testDeviceLoginScreen() {
        let app = launchApp(["--login"])
        XCTAssertTrue(app.staticTexts["seplis.net/device"].waitForExistence(timeout: 10))
        XCTAssertTrue(app.images["SEPLIS"].exists)
        XCTAssertTrue(app.staticTexts["Then enter this code"].exists)
        XCTAssertTrue(app.staticTexts["Sign-in code 123456"].exists)
        attachScreenshot("Device login")
    }
}
