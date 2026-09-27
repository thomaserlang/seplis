import XCTest
@testable import seplis_apple_tv

nonisolated final class SessionStateTests: XCTestCase {
    @MainActor func testEmptyStoreTransitionsFromRestoringToSignedOut() async {
        let session = AppSession(store: MemoryProfileStore())
        guard case .restoring = session.state else { return XCTFail("Expected restoring") }
        await session.restore()
        guard case .signedOut = session.state else { return XCTFail("Expected signed out") }
    }

    @MainActor func testRestoreFailureCanBeRetried() async {
        let store = MemoryProfileStore()
        store.loadFailure = true
        let session = AppSession(store: store)
        await session.restore()
        guard case .restoreFailed = session.state else { return XCTFail("Expected restore failure") }
        store.loadFailure = false
        await session.restore()
        guard case .signedOut = session.state else { return XCTFail("Expected signed out after retry") }
    }

    @MainActor func testRemovingLastExpiredProfileReturnsToLogin() async {
        let store = MemoryProfileStore()
        let user = CurrentUser(id: 1, username: "Alex")
        store.snapshot.profiles = [.init(user: user, token: nil)]
        let session = AppSession(store: store)
        await session.restore()
        guard case .choosingProfile = session.state else { return XCTFail("Expected profile picker") }
        session.removeProfile(user)
        guard case .signedOut = session.state else { return XCTFail("Expected login after removal") }
    }

    @MainActor func testUnavailablePendingSignInKeepsProfileRecoveryAccessible() async {
        let store = MemoryProfileStore()
        store.snapshot.pendingToken = "pending-token"
        let transport = stubSession { _ in (503, Data()) }
        let session = AppSession(store: store, makeClient: { APIClient(token: $0, session: transport) })
        await session.restore()
        guard case .choosingProfile = session.state else { return XCTFail("Expected profile recovery") }
        XCTAssertTrue(session.hasPendingSignIn)
        StubURLProtocol.handler.withLock { $0 = { _ in (401, Data()) } }
        await session.retryPendingSignIn()
        guard case .signedOut = session.state else { return XCTFail("Expected login after retry rejects token") }
    }

    @MainActor func testRejectedPendingSignInReturnsToLogin() async {
        let store = MemoryProfileStore()
        store.snapshot.pendingToken = "expired-token"
        let transport = stubSession { _ in (401, Data()) }
        let session = AppSession(store: store, makeClient: { APIClient(token: $0, session: transport) })
        await session.restore()
        guard case .signedOut = session.state else { return XCTFail("Expected login after expired token") }
        XCTAssertFalse(session.hasPendingSignIn)
    }
}
