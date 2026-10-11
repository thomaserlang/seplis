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
    private var loadedPageCount = 0

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
            if generation == request {
                isLoading = false
                isLoadingMore = false
            }
        }
        do {
            var refreshedItems: [HomeItem] = []
            var nextCursor = more ? cursor : nil
            var fetchedPageCount = 0
            // Refresh the loaded range atomically so later-page focus targets stay mounted.
            for _ in 0..<(more ? 1 : max(1, loadedPageCount)) {
                let page = try await fetchPage(cursor: nextCursor)
                try Task.checkCancellation()
                guard generation == request else { return }
                refreshedItems.append(contentsOf: page.items)
                nextCursor = page.cursor
                fetchedPageCount += 1
                if nextCursor == nil { break }
            }
            var seen = Set<String>()
            items = ((more ? items : []) + refreshedItems).filter { seen.insert($0.id).inserted }
            cursor = nextCursor
            loadedPageCount = (more ? loadedPageCount : 0) + fetchedPageCount
            hasLoaded = true
        } catch is CancellationError {
        } catch let error as URLError where error.code == .cancelled {
        } catch {
            if generation == request { self.error = error.localizedDescription }
        }
    }

    private func fetchPage(cursor: String?) async throws -> (items: [HomeItem], cursor: String?) {
        var query = shelf.query
        if let cursor { query.append(.init(name: "cursor", value: cursor)) }
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
        return (newItems, nextCursor)
    }

    func loadMoreIfNeeded(near itemID: String) async {
        guard error == nil, items.suffix(8).contains(where: { $0.id == itemID }) else { return }
        await load(more: true)
    }
}
