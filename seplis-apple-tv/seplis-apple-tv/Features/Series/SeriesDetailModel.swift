import Foundation
import Observation

@MainActor @Observable
final class SeriesDetailModel {
    let reference: MediaReference
    private(set) var media: Series?
    private(set) var nextEpisode: Episode?
    private(set) var lastEpisode: Episode?
    private(set) var isLoading = false
    private(set) var isUpdating = false
    var error: String?
    private let api: APIClient

    init(reference: MediaReference, api: APIClient) {
        self.reference = reference
        self.api = api
    }

    func load() async {
        guard !isLoading else { return }
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            let loaded: Series = try await api.get(reference.path, query: [
                .init(name: "expand", value: "user_watchlist,user_favorite")
            ])
            async let next: Episode? = api.getOptional("\(reference.path)/episode-to-watch")
            async let last: Episode? = api.getOptional("\(reference.path)/episode-last-watched")
            (nextEpisode, lastEpisode) = try await (next, last)
            media = loaded
        } catch is CancellationError {
        } catch let error as URLError where error.code == .cancelled {
        } catch { self.error = error.localizedDescription }
    }

    func toggleWatchlist() async {
        await update("watchlist", method: media?.userWatchlist?.onWatchlist == true ? "DELETE" : "PUT")
    }

    func toggleFavorite() async {
        await update("favorite", method: media?.userFavorite?.favorite == true ? "DELETE" : "PUT")
    }

    func changeWatched(increment: Bool, episode: Episode) async {
        await update("episodes/\(episode.number)/watched", method: increment ? "POST" : "DELETE")
    }

    private func update(_ path: String, method: String) async {
        guard !isUpdating else { return }
        isUpdating = true
        defer { isUpdating = false }
        do {
            try await api.perform("\(reference.path)/\(path)", method: method)
            if path.hasSuffix("watched") {
                NotificationCenter.default.post(name: .watchHistoryDidChange, object: nil)
            }
            await load()
        } catch { self.error = error.localizedDescription }
    }
}
