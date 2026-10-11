import Foundation
import Observation

@MainActor @Observable
final class CastRowModel {
    private(set) var members: [CastMember] = []
    private(set) var cursor: String?
    private(set) var isLoading = false
    private(set) var hasLoaded = false
    private(set) var error: String?

    func load(reference: MediaReference, api: APIClient, more: Bool = false) async {
        guard !isLoading, !more || cursor != nil else { return }
        isLoading = true
        error = nil
        defer { isLoading = false }
        do {
            var query = [URLQueryItem(name: "per_page", value: "25")]
            if more, let cursor { query.append(.init(name: "cursor", value: cursor)) }
            let pageMembers: [CastMember]
            let nextCursor: String?
            switch reference.kind {
            case .movie:
                let page: Page<MovieCastCredit> = try await api.get("\(reference.path)/cast", query: query)
                pageMembers = page.records.map(\.member)
                nextCursor = page.cursor
            case .series:
                let page: Page<SeriesCastCredit> = try await api.get("\(reference.path)/cast", query: query)
                pageMembers = page.records.map(\.member)
                nextCursor = page.cursor
            }
            try Task.checkCancellation()
            var seen = Set<Int>()
            members = ((more ? members : []) + pageMembers).filter { seen.insert($0.id).inserted }
            cursor = nextCursor
            hasLoaded = true
        } catch is CancellationError {
        } catch let error as URLError where error.code == .cancelled {
        } catch { self.error = error.localizedDescription }
    }
}
