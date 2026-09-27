import Foundation
import Observation

@MainActor @Observable
final class PlaybackProgress {
    private(set) var completed = false
    private(set) var error: String?
    private var lastSaved: Double
    private var pending: Task<Void, Never>?
    private let api: APIClient
    private let path: String

    init(api: APIClient, path: String, start: Double) {
        self.api = api
        self.path = path
        lastSaved = start
    }

    func record(position: Double, duration: Double) {
        guard position.isFinite, position >= 0, duration.isFinite, duration > 0, !completed else { return }
        let finished = position >= duration * 0.9
        guard finished || abs(position - lastSaved) >= 10 else { return }
        lastSaved = position
        if finished { completed = true }
        let previous = pending
        pending = Task {
            // Serialize writes so an older position can never overwrite completion.
            await previous?.value
            do {
                if finished {
                    try await api.perform("\(path)/watched", method: "POST")
                } else {
                    try await api.perform("\(path)/watched-position", method: "PUT",
                                          body: APIClient.body(["position": min(86400, Int(position.rounded()))]))
                }
                error = nil
            } catch {
                // Watched increments are not idempotent; do not retry an ambiguous response.
                self.error = "Could not save watch progress. \(error.localizedDescription)"
            }
        }
    }

    func flush() async { await pending?.value }
}
