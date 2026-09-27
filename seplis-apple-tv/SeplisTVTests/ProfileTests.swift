import XCTest
@testable import seplis_apple_tv

nonisolated final class ProfileTests: XCTestCase {
    private let first = CurrentUser(id: 1, username: "Alex")
    private let second = CurrentUser(id: 2, username: "Sam")

    @MainActor private func store() -> MemoryProfileStore {
        let store = MemoryProfileStore()
        store.snapshot = ProfileSnapshot(profiles: [.init(user: first, token: "one"), .init(user: second, token: "two")],
                                         activeUserID: 1)
        return store
    }

    @MainActor func testSwitchPersistsActiveProfileAndReplacesClient() async {
        let store = store()
        let session = AppSession(store: store)
        await session.restore()
        let oldID = session.sessionID
        session.switchProfile(second)
        XCTAssertEqual(session.user, second)
        XCTAssertEqual(store.snapshot.activeUserID, 2)
        XCTAssertNotEqual(session.sessionID, oldID)
        let restored = AppSession(store: store)
        await restored.restore()
        XCTAssertEqual(restored.user, second)
    }

    @MainActor func testRemoveActiveProfileFallsBackToOtherAccount() async {
        let store = store()
        let session = AppSession(store: store)
        await session.restore()
        session.removeProfile(first)
        XCTAssertEqual(session.user, second)
        XCTAssertEqual(session.profiles.count, 1)
        session.removeProfile(second)
        XCTAssertNil(session.api)
        XCTAssertTrue(session.profiles.isEmpty)
    }

    @MainActor func testOldUnauthorizedResponseDoesNotSignOutNewProfile() async {
        let session = AppSession(store: store())
        await session.restore()
        let oldClient = session.api
        session.switchProfile(second)
        oldClient?.onUnauthorized?()
        XCTAssertEqual(session.user, second)
        XCTAssertTrue(session.needsSignIn(first))
        XCTAssertFalse(session.needsSignIn(second))
    }

    @MainActor func testFailedProfileLookupKeepsOneTimeTokenAndExistingAccount() async {
        let store = store()
        let transport = stubSession { _ in (503, Data()) }
        let session = AppSession(store: store, makeClient: { APIClient(token: $0, session: transport) })
        await session.restore()
        do { try await session.signIn(token: "new-one-time-token"); XCTFail("Expected a server failure") }
        catch {}
        XCTAssertEqual(store.snapshot.pendingToken, "new-one-time-token")
        XCTAssertEqual(session.user, first)
        XCTAssertEqual(session.profiles.count, 2)
    }

    @MainActor func testAddingSameAccountReplacesTokenWithoutDuplicate() async throws {
        let store = store()
        let transport = stubSession { _ in (200, Data("{\"id\":1,\"username\":\"Alex\"}".utf8)) }
        let session = AppSession(store: store, makeClient: { APIClient(token: $0, session: transport) })
        await session.restore()
        let obsoleteClient = session.api
        try await session.signIn(token: "new-token")
        obsoleteClient?.onUnauthorized?()
        XCTAssertEqual(session.profiles.count, 2)
        XCTAssertEqual(store.snapshot.profiles.first { $0.user.id == 1 }?.token, "new-token")
        XCTAssertEqual(session.user, first)
        XCTAssertNil(store.snapshot.pendingToken)
    }

    @MainActor func testStorageFailureLeavesActiveAccountUntouched() async {
        let store = store()
        let session = AppSession(store: store)
        await session.restore()
        store.failure = true
        session.switchProfile(second)
        XCTAssertEqual(session.user, first)
        XCTAssertNotNil(session.error)
    }
}
