import Synchronization
import XCTest
@testable import seplis_apple_tv

nonisolated final class DeviceLoginTests: XCTestCase {
    private static func authorization(expires: String = "2099-01-01T00:00:00Z") -> Data {
        Data("""
        {"device_code":"fixture-code","user_code":"001234","verification_uri":"https://seplis.net/tv",
         "verification_uri_complete":"https://seplis.net/tv?code=001234","expires_at":"\(expires)","poll_interval_seconds":1}
        """.utf8)
    }

    @MainActor func testPendingThenAuthorizedAddsProfile() async {
        let polls = Mutex(0)
        let transport = stubSession { request in
            switch request.url!.path {
            case "/2/device-authorization": return (201, Self.authorization())
            case "/2/device-authorization/token":
                let count = polls.withLock { $0 += 1; return $0 }
                return (200, Data((count == 1 ? "{\"status\":\"pending\"}" : "{\"status\":\"authorized\",\"access_token\":\"new-token\"}").utf8))
            case "/2/users/me": return (200, Data("{\"id\":3,\"username\":\"New account\"}".utf8))
            default: throw URLError(.badURL)
            }
        }
        let store = MemoryProfileStore()
        let session = AppSession(store: store, makeClient: { APIClient(token: $0, session: transport) })
        let model = DeviceLoginModel(api: APIClient(session: transport))
        await model.run(session: session)
        XCTAssertNil(model.error)
        XCTAssertEqual(session.user?.id, 3)
        XCTAssertEqual(store.snapshot.profiles.first?.token, "new-token")
        XCTAssertEqual(polls.withLock { $0 }, 2)
    }

    @MainActor func testExpiredCodeDoesNotPoll() async {
        let calls = Mutex(0)
        let transport = stubSession { _ in
            calls.withLock { $0 += 1 }
            return (201, Self.authorization(expires: "2000-01-01T00:00:00Z"))
        }
        let model = DeviceLoginModel(api: APIClient(session: transport))
        await model.run(session: AppSession(store: MemoryProfileStore()))
        XCTAssertTrue(model.expired)
        XCTAssertEqual(calls.withLock { $0 }, 1)
    }

    @MainActor func testCancellationStopsPollingWithoutDisplayingError() async throws {
        let calls = Mutex(0)
        let transport = stubSession { _ in calls.withLock { $0 += 1 }; return (201, Self.authorization()) }
        let model = DeviceLoginModel(api: APIClient(session: transport))
        let task = Task { await model.run(session: AppSession(store: MemoryProfileStore())) }
        try await Task.sleep(for: .milliseconds(100))
        task.cancel()
        await task.value
        XCTAssertEqual(calls.withLock { $0 }, 1)
        XCTAssertNil(model.error)
    }
}
