import Foundation
import Observation

@MainActor @Observable
final class MediaDetailModel {
    let reference: MediaReference
    private(set) var media: Media?
    private(set) var nextEpisode: Episode?
    private(set) var lastEpisode: Episode?
    private(set) var canPlayMovie = false
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
            let expand = reference.kind == .movie
                ? "user_watchlist,user_favorite,user_watched" : "user_watchlist,user_favorite"
            let loadedMedia: Media = try await api.get(reference.path, query: [.init(name: "expand", value: expand)])
            if reference.kind == .series {
                async let next: Episode? = api.getOptional("\(reference.path)/episode-to-watch")
                async let last: Episode? = api.getOptional("\(reference.path)/episode-last-watched")
                (nextEpisode, lastEpisode) = try await (next, last)
            } else {
                let requests: [PlayRequest] = try await api.get("\(reference.path)/play-servers")
                canPlayMovie = !requests.isEmpty
            }
            media = loadedMedia
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

    func changeWatched(increment: Bool, episode: Episode? = nil) async {
        let path = episode.map { "episodes/\($0.number)/watched" } ?? "watched"
        await update(path, method: increment ? "POST" : "DELETE")
    }

    private func update(_ path: String, method: String) async {
        guard !isUpdating else { return }
        isUpdating = true
        defer { isUpdating = false }
        do {
            try await api.perform("\(reference.path)/\(path)", method: method)
            await load()
        } catch { self.error = error.localizedDescription }
    }
}
