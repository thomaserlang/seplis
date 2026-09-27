import Foundation
import Observation

nonisolated struct SearchResult: Decodable {
    let type: MediaKind
    let id: Int
    let title: String?
    let posterImage: Poster?
}

@MainActor @Observable
final class SearchModel {
    private(set) var results: [SearchResult] = []
    private(set) var isLoading = false
    private(set) var error: String?
    private var generation = UUID()

    func search(_ text: String, api: APIClient) async {
        let request = UUID()
        generation = request
        results = []
        error = nil
        let query = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else { isLoading = false; return }
        isLoading = true
        defer { if generation == request { isLoading = false } }
        do {
            try await Task.sleep(for: .milliseconds(300))
            let response: [SearchResult] = try await api.get("search", query: [
                .init(name: "query", value: query), .init(name: "limit", value: "60"),
            ])
            try Task.checkCancellation()
            guard generation == request else { return }
            results = response
        } catch is CancellationError {
        } catch let error as URLError where error.code == .cancelled {
        } catch { if generation == request { self.error = error.localizedDescription } }
    }
}
