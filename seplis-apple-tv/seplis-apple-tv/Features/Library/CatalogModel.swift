import Foundation
import Observation

@MainActor @Observable
final class CatalogModel {
    private(set) var items: [MediaSummary] = []
    private(set) var cursor: String?
    private(set) var isLoading = false
    private(set) var error: String?
    private var generation = UUID()

    func load(api: APIClient, kind: MediaKind, filters: CatalogFilters, more: Bool = false) async {
        if more && (isLoading || cursor == nil) { return }
        let request = UUID()
        generation = request
        isLoading = true
        error = nil
        var query = filters.query(kind: kind)
        if more, let cursor { query.append(.init(name: "cursor", value: cursor)) }
        else { items = []; cursor = nil }
        defer { if generation == request { isLoading = false } }
        do {
            let page: Page<MediaSummary> = try await api.get(kind.path, query: query)
            try Task.checkCancellation()
            guard generation == request else { return }
            var seen = Set<Int>()
            items = (items + page.records).filter { seen.insert($0.id).inserted }
            cursor = page.cursor
        } catch is CancellationError {
        } catch let error as URLError where error.code == .cancelled {
        } catch { if generation == request { self.error = error.localizedDescription } }
    }
}
