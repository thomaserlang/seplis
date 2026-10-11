import SwiftUI

struct AppResumePolicy {
    static let resetInterval: Duration = .seconds(15 * 60)
    private var backgroundedAt: ContinuousClock.Instant?

    mutating func shouldReset(for phase: ScenePhase, now: ContinuousClock.Instant = .now) -> Bool {
        switch phase {
        case .background:
            if backgroundedAt == nil { backgroundedAt = now }
            return false
        case .active:
            defer { backgroundedAt = nil }
            guard let backgroundedAt else { return false }
            return backgroundedAt.duration(to: now) >= Self.resetInterval
        default:
            return false
        }
    }
}
