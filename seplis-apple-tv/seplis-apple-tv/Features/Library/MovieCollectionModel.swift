import Foundation
import Observation

@MainActor @Observable
final class MovieCollectionModel {
    private(set) var movies: [Media] = []
    private(set) var cursor: String?
    private(set) var isLoading = false
    private(set) var hasLoaded = false
    private(set) var error: String?

    func load(collectionID: Int, api: APIClient, more: Bool = false) async {
        guard !isLoading, !more || cursor != nil else { return }
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            var query: [URLQueryItem] = [
                .init(name: "collection_id", value: String(collectionID)),
                .init(name: "sort", value: "release_date_asc"),
                .init(name: "per_page", value: "24"),
            ]
            if more, let cursor { query.append(.init(name: "cursor", value: cursor)) }
            let page: Page<Media> = try await api.get("movies", query: query)
            try Task.checkCancellation()
            var seen = Set<Int>()
            movies = ((more ? movies : []) + page.records).filter { seen.insert($0.id).inserted }
            cursor = page.cursor
            hasLoaded = true
        } catch is CancellationError {
        } catch let error as URLError where error.code == .cancelled {
        } catch { self.error = error.localizedDescription }
    }
}
