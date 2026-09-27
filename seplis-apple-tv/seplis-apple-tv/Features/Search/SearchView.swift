import SwiftUI

struct SearchView: View {
    let api: APIClient
    @State private var query = ""
    @State private var loadedQuery: String?
    @State private var model = SearchModel()
    @State private var selectedMedia: MediaReference?

    var body: some View {
        NavigationStack {
            ScrollView {
                MediaPosterGrid(items: model.results.map {
                    .init(reference: .init(kind: $0.type, id: $0.id), title: $0.title ?? "Untitled", poster: $0.posterImage)
                }, isLoading: model.isLoading, select: { selectedMedia = $0 })
                if let error = model.error {
                    FailureView(message: error) { Task { await model.search(query, api: api) } }
                } else if !model.isLoading && model.results.isEmpty && !query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    ContentUnavailableView.search(text: query)
                }
            }
            .background(LibraryStyle.background.ignoresSafeArea())
            .searchable(text: $query, prompt: "Search movies and series")
        }
        .task(id: query) {
            guard loadedQuery != query else { return }
            let requestedQuery = query
            await model.search(query, api: api)
            if !Task.isCancelled { loadedQuery = requestedQuery }
        }
        .modifier(MediaDetailPresentation(reference: $selectedMedia, api: api))
    }
}
