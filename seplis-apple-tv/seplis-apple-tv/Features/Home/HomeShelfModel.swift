import Foundation
import Observation

@MainActor @Observable
final class HomeShelfModel: Identifiable {
    let shelf: HomeShelf
    var id: Int { shelf.id }
    private(set) var items: [HomeItem] = []
    private(set) var cursor: String?
    private(set) var isLoading = false
    private(set) var isLoadingMore = false
    private(set) var hasLoaded = false
    private(set) var error: String?
    private let api: APIClient
    private var generation = UUID()

    init(shelf: HomeShelf, api: APIClient) {
        self.shelf = shelf
        self.api = api
    }

    func load(more: Bool = false) async {
        guard !more || !isLoading else { return }
        guard !more || cursor != nil else { return }
        isLoading = true
        isLoadingMore = more
        let request = UUID()
        generation = request
        error = nil
        defer {
            if generation == request { isLoading = false; isLoadingMore = false }
        }
        do {
            var query = shelf.query
            if more, let cursor { query.append(.init(name: "cursor", value: cursor)) }
            let newItems: [HomeItem]
            let nextCursor: String?
            switch shelf {
            case .watched:
                let page: Page<WatchedRecord> = try await api.get(shelf.path, query: query)
                newItems = page.records.map {
                    HomeItem(reference: .init(kind: $0.type, id: $0.data.id), media: $0.data)
                }
                nextCursor = page.cursor
            case .toWatch, .recentlyAired:
                let page: Page<SeriesEpisodeRecord> = try await api.get(shelf.path, query: query)
                newItems = page.records.map {
                    HomeItem(reference: .init(kind: .series, id: $0.series.id),
                             media: $0.series, episode: $0.episode)
                }
                nextCursor = page.cursor
            default:
                let page: Page<MediaSummary> = try await api.get(shelf.path, query: query)
                newItems = page.records.map {
                    HomeItem(reference: .init(kind: shelf.kind, id: $0.id), media: $0)
                }
                nextCursor = page.cursor
            }
            try Task.checkCancellation()
            guard generation == request else { return }
            var seen = Set<String>()
            items = ((more ? items : []) + newItems).filter { seen.insert($0.id).inserted }
            cursor = nextCursor
            hasLoaded = true
        } catch is CancellationError {
        } catch let error as URLError where error.code == .cancelled {
        } catch {
            if generation == request { self.error = error.localizedDescription }
        }
    }

    func loadMoreIfNeeded(near itemID: String) async {
        guard error == nil, items.suffix(8).contains(where: { $0.id == itemID }) else { return }
        await load(more: true)
    }
}
