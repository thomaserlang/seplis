import Foundation
import Observation

@MainActor @Observable
final class AppSession {
    private(set) var state: SessionState = .restoring
    var error: String?
    private var snapshot = ProfileSnapshot()
    private let store: any ProfileStore
    private let makeClient: (String) -> APIClient
    let authorizationAPI: APIClient

    var profiles: [CurrentUser] { snapshot.profiles.map(\.user) }
    var hasPendingSignIn: Bool { snapshot.pendingToken != nil }

    private var authenticatedSession: AuthenticatedSession? {
        guard case .authenticated(let session) = state else { return nil }
        return session
    }

    var user: CurrentUser? { authenticatedSession?.user }
    var api: APIClient? { authenticatedSession?.api }
    var sessionID: UUID? { authenticatedSession?.id }

    init(store: any ProfileStore = KeychainProfileStore(), authorizationAPI: APIClient = APIClient(),
         makeClient: @escaping (String) -> APIClient = { APIClient(token: $0) }) {
        self.store = store
        self.authorizationAPI = authorizationAPI
        self.makeClient = makeClient
    }

    func restore() async {
        state = .restoring
        error = nil
        do {
            snapshot = try store.load()
        } catch {
            state = .restoreFailed
            self.error = error.localizedDescription
            return
        }

        guard let token = snapshot.pendingToken else {
            activateCurrentProfile()
            return
        }
        do {
            try await completeSignIn(token: token)
        } catch {
            activateCurrentProfile()
            self.error = error.localizedDescription
        }
    }

    func signIn(token: String) async throws {
        // The device endpoint returns its token only once. Keep it even if /users/me is offline.
        var updated = snapshot
        updated.pendingToken = token
        try persist(updated)
        try await completeSignIn(token: token)
    }

    func retryPendingSignIn() async {
        guard let token = snapshot.pendingToken else { return }
        do { try await completeSignIn(token: token) }
        catch {
            if case .choosingProfile = state { activateCurrentProfile() }
            self.error = error.localizedDescription
        }
    }

    private func completeSignIn(token: String) async throws {
        let profile: CurrentUser
        do {
            profile = try await makeClient(token).get("users/me")
        } catch let error as APIError where error.statusCode == 401 {
            var updated = snapshot
            updated.pendingToken = nil
            try persist(updated)
            throw error
        }
        var updated = snapshot
        updated.profiles.removeAll { $0.user.id == profile.id }
        updated.profiles.append(StoredProfile(user: profile, token: token))
        updated.activeUserID = profile.id
        updated.pendingToken = nil
        try persist(updated)
        activateCurrentProfile()
        error = nil
    }

    func needsSignIn(_ profile: CurrentUser) -> Bool {
        snapshot.profiles.first { $0.user.id == profile.id }?.token == nil
    }

    func switchProfile(_ profile: CurrentUser) {
        guard !needsSignIn(profile) else { return }
        do {
            var updated = snapshot
            updated.activeUserID = profile.id
            try persist(updated)
            activateCurrentProfile()
        } catch { self.error = error.localizedDescription }
    }

    func removeProfile(_ profile: CurrentUser) {
        do {
            var updated = snapshot
            updated.profiles.removeAll { $0.user.id == profile.id }
            if updated.activeUserID == profile.id {
                updated.activeUserID = updated.profiles.first { $0.token != nil }?.user.id
            }
            try persist(updated)
            if user == nil || user?.id == profile.id { activateCurrentProfile() }
        } catch { self.error = error.localizedDescription }
    }

    private func expireProfile(id: Int, token: String) {
        guard let index = snapshot.profiles.firstIndex(where: { $0.user.id == id && $0.token == token }) else { return }
        do {
            var updated = snapshot
            updated.profiles[index].token = nil
            if updated.activeUserID == id { updated.activeUserID = nil }
            try persist(updated)
            if user?.id == id { activateCurrentProfile() }
        } catch { self.error = error.localizedDescription }
    }

    private func activateCurrentProfile() {
        guard let stored = snapshot.profiles.first(where: { $0.user.id == snapshot.activeUserID }),
              let token = stored.token else {
            state = snapshot.profiles.isEmpty && !hasPendingSignIn ? .signedOut : .choosingProfile
            return
        }
        let client = makeClient(token)
        client.accountID = stored.user.id
        client.onUnauthorized = { [weak self] in self?.expireProfile(id: stored.user.id, token: token) }
        state = .authenticated(AuthenticatedSession(user: stored.user, api: client))
    }

    private func persist(_ updated: ProfileSnapshot) throws {
        try store.save(updated)
        snapshot = updated
    }
}
