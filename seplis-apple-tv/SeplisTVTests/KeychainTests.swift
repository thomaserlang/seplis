import Security
import XCTest
@testable import seplis_apple_tv

nonisolated final class KeychainTests: XCTestCase {
    @MainActor func testProfilesPersistInRealSimulatorKeychain() throws {
        let service = "net.seplis.tv.tests.\(UUID().uuidString)"
        let store = KeychainProfileStore(service: service)
        defer {
            SecItemDelete([
                kSecClass as String: kSecClassGenericPassword,
                kSecAttrService as String: service,
            ] as CFDictionary)
        }
        XCTAssertTrue(try store.load().profiles.isEmpty)
        let profile = StoredProfile(user: CurrentUser(id: 10, username: "Keychain test"), token: "fixture-token")
        try store.save(ProfileSnapshot(profiles: [profile], activeUserID: 10))
        let saved = try KeychainProfileStore(service: service).load()
        XCTAssertEqual(saved.profiles.first?.token, "fixture-token")
        XCTAssertEqual(saved.activeUserID, 10)
        try store.save(ProfileSnapshot())
        XCTAssertTrue(try store.load().profiles.isEmpty)
    }
}
