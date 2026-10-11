import XCTest
@testable import seplis_apple_tv

nonisolated final class AppResumePolicyTests: XCTestCase {
    @MainActor func testInactiveInterruptionDoesNotResetBrowsing() {
        var policy = AppResumePolicy()
        let now = ContinuousClock.now
        XCTAssertFalse(policy.shouldReset(for: .active, now: now))
        XCTAssertFalse(policy.shouldReset(for: .inactive, now: now))
        XCTAssertFalse(policy.shouldReset(for: .active, now: now.advanced(by: .seconds(3600))))
    }

    @MainActor func testShortAbsencePreservesBrowsingAndStartsANewInterval() {
        var policy = AppResumePolicy()
        let now = ContinuousClock.now
        XCTAssertFalse(policy.shouldReset(for: .background, now: now))
        XCTAssertFalse(policy.shouldReset(for: .active, now: now.advanced(by: .seconds(60))))
        XCTAssertFalse(policy.shouldReset(for: .background, now: now.advanced(by: .seconds(1200))))
        XCTAssertFalse(policy.shouldReset(for: .active, now: now.advanced(by: .seconds(1260))))
    }

    @MainActor func testLongAbsenceResetsOnceIncludingURLBeforeActivation() {
        var policy = AppResumePolicy()
        let now = ContinuousClock.now
        XCTAssertFalse(policy.shouldReset(for: .background, now: now))
        XCTAssertFalse(policy.shouldReset(for: .inactive, now: now.advanced(by: .seconds(900))))
        // A deep link consumes the reset first; subsequent activation must preserve its destination.
        XCTAssertTrue(policy.shouldReset(for: .active, now: now.advanced(by: AppResumePolicy.resetInterval)))
        XCTAssertFalse(policy.shouldReset(for: .active, now: now.advanced(by: .seconds(901))))
    }

    @MainActor func testRepeatedBackgroundNotificationsDoNotPostponeReset() {
        var policy = AppResumePolicy()
        let now = ContinuousClock.now
        XCTAssertFalse(policy.shouldReset(for: .background, now: now))
        XCTAssertFalse(policy.shouldReset(for: .background, now: now.advanced(by: .seconds(800))))
        XCTAssertTrue(policy.shouldReset(for: .active, now: now.advanced(by: .seconds(901))))
    }
}
