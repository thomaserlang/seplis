import XCTest

nonisolated class UITestCase: XCTestCase {
    @MainActor func launchApp(_ arguments: [String] = []) -> XCUIApplication {
        let app = XCUIApplication()
        app.launchArguments = ["--ui-testing"] + arguments
        app.launch()
        return app
    }

    @MainActor func select(_ element: XCUIElement, in app: XCUIApplication) {
        for _ in 0..<15 {
            if element.hasFocus { break }
            let focused = app.descendants(matching: .any).matching(NSPredicate(format: "hasFocus == true")).firstMatch
            guard focused.exists else { XCUIRemote.shared.press(.down); continue }
            let target = element.frame
            let current = focused.frame
            // A native List focuses its row container rather than the nested NavigationLink.
            if current.contains(CGPoint(x: target.midX, y: target.midY)) { break }
            if element.identifier.hasPrefix("filter-category-"), current.minX > target.maxX {
                XCUIRemote.shared.press(.left)
            } else if abs(target.midY - current.midY) > 50 {
                XCUIRemote.shared.press(target.midY > current.midY ? .down : .up)
            } else {
                XCUIRemote.shared.press(target.midX > current.midX ? .right : .left)
            }
        }
        let focused = app.descendants(matching: .any).matching(NSPredicate(format: "hasFocus == true")).firstMatch
        let center = CGPoint(x: element.frame.midX, y: element.frame.midY)
        XCTAssertTrue(element.hasFocus || (focused.exists && focused.frame.contains(center)), "Could not focus \(element.label)")
        XCUIRemote.shared.press(.select)
    }

    @MainActor func attachScreenshot(_ name: String) {
        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = name
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
