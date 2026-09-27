import Foundation
import Security

nonisolated struct CurrentUser: Codable, Identifiable, Equatable {
    let id: Int
    let username: String
}

nonisolated struct StoredProfile: Codable {
    var user: CurrentUser
    var token: String?
}

nonisolated struct ProfileSnapshot: Codable {
    var profiles: [StoredProfile] = []
    var activeUserID: Int?
    var pendingToken: String?
}

protocol ProfileStore {
    func load() throws -> ProfileSnapshot
    func save(_ snapshot: ProfileSnapshot) throws
}

struct KeychainProfileStore: ProfileStore {
    let service: String

    init(service: String = "net.seplis.tv") { self.service = service }

    private var query: [String: Any] { [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: service,
        kSecAttrAccount as String: "profiles",
    ] }

    func load() throws -> ProfileSnapshot {
        var lookup = query
        lookup[kSecReturnData as String] = true
        lookup[kSecMatchLimit as String] = kSecMatchLimitOne
        var result: CFTypeRef?
        let status = SecItemCopyMatching(lookup as CFDictionary, &result)
        if status == errSecItemNotFound { return ProfileSnapshot() }
        try check(status)
        guard let data = result as? Data else { throw APIError.message("Saved profiles could not be read.") }
        return try JSONDecoder().decode(ProfileSnapshot.self, from: data)
    }

    func save(_ snapshot: ProfileSnapshot) throws {
        let attributes: [String: Any] = [
            kSecValueData as String: try JSONEncoder().encode(snapshot),
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly,
        ]
        let status = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        if status == errSecItemNotFound {
            try check(SecItemAdd(query.merging(attributes) { _, new in new } as CFDictionary, nil))
        } else {
            try check(status)
        }
    }

    private func check(_ status: OSStatus) throws {
        guard status == errSecSuccess else {
            throw APIError.message("Secure profile storage is unavailable (\(status)).")
        }
    }
}
