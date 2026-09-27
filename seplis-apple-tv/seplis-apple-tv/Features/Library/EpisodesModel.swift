import Foundation
import Observation

@MainActor @Observable
final class EpisodesModel {
    private(set) var episodes: [Episode] = []
    private(set) var isLoading = false
    var error: String?
    private(set) var isUpdating = false
    var updateError: String?

    func changeWatched(reference: MediaReference, episode: Episode, increment: Bool,
                       season: Int?, api: APIClient) async {
        guard !isUpdating else { return }
        isUpdating = true
        defer { isUpdating = false }
        do {
            try await api.perform("\(reference.path)/episodes/\(episode.number)/watched",
                                  method: increment ? "POST" : "DELETE")
            NotificationCenter.default.post(name: .watchHistoryDidChange, object: nil)
            await load(reference: reference, season: season, api: api)
        } catch { updateError = error.localizedDescription }
    }

    func load(reference: MediaReference, season: Int?, api: APIClient) async {
        guard !isLoading else { return }
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            var result: [Episode] = []
            var cursor: String?
            repeat {
                var query: [URLQueryItem] = [
                    .init(name: "expand", value: "user_watched,user_can_watch"),
                    .init(name: "per_page", value: "100"),
                ]
                if let season { query.append(.init(name: "season", value: String(season))) }
                if let cursor { query.append(.init(name: "cursor", value: cursor)) }
                let page: Page<Episode> = try await api.get("\(reference.path)/episodes", query: query)
                result += page.records
                cursor = page.cursor
                try Task.checkCancellation()
            } while cursor != nil
            episodes = result
        } catch is CancellationError {
        } catch let error as URLError where error.code == .cancelled {
        } catch { self.error = error.localizedDescription }
    }
}
