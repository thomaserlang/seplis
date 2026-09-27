import Foundation

enum SessionState {
    case restoring
    case restoreFailed
    case signedOut
    case choosingProfile
    case authenticated(AuthenticatedSession)
}

struct AuthenticatedSession: Identifiable {
    let id = UUID()
    let user: CurrentUser
    let api: APIClient
}
