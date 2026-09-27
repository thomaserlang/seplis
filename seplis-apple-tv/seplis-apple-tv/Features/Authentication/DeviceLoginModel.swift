import Foundation
import Observation

@MainActor @Observable
final class DeviceLoginModel {
    private(set) var authorization: DeviceAuthorization?
    private(set) var error: String?
    private(set) var expired = false
    private let api: APIClient
    private var receivedToken: String?

    init(api: APIClient = APIClient()) { self.api = api }

    func run(session: AppSession) async {
        error = nil
        do {
            if let receivedToken {
                try await session.signIn(token: receivedToken)
                return
            }
            if authorization == nil || expired {
                authorization = try await api.send("device-authorization", method: "POST")
                expired = false
            }
            guard let authorization else { return }
            while Date() < authorization.expiresAt {
                try await Task.sleep(for: .seconds(max(1, authorization.pollIntervalSeconds)))
                try Task.checkCancellation()
                let response: DeviceTokenResponse = try await api.send(
                    "device-authorization/token", method: "POST",
                    body: APIClient.body(DeviceTokenRequest(deviceCode: authorization.deviceCode)))
                if response.status == "authorized" {
                    guard let token = response.accessToken, !token.isEmpty else {
                        throw APIError.invalidResponse
                    }
                    receivedToken = token
                    try await session.signIn(token: token)
                    return
                }
                guard response.status == "pending" else { throw APIError.invalidResponse }
            }
            expired = true
            error = "This code has expired. Request a new code."
        } catch is CancellationError {
        } catch let error as URLError where error.code == .cancelled {
        } catch {
            if (error as? APIError)?.statusCode == 401 {
                receivedToken = nil
                expired = true
            }
            if let apiError = error as? APIError,
               [404, 410].contains(apiError.statusCode ?? 0) { expired = true }
            self.error = error.localizedDescription
        }
    }
}
