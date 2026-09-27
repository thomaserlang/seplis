import Foundation

nonisolated struct DeviceAuthorization: Decodable {
    let deviceCode: String
    let userCode: String
    let verificationUri: URL
    let verificationUriComplete: URL
    let expiresAt: Date
    let pollIntervalSeconds: Int
}

nonisolated struct DeviceTokenResponse: Decodable {
    let status: String
    let accessToken: String?
}

nonisolated struct DeviceTokenRequest: Encodable {
    let deviceCode: String
}
