import SwiftUI

struct CatalogView: View {
    let api: APIClient
    let kind: MediaKind
    @State private var showsFilters = false
    let enteringFromMenu: Bool
    @State private var model = CatalogModel()
    @State private var filters = CatalogFilters()
    @State private var revision = 0
    @State private var loadedRevision: Int?
    @State private var selectedMedia: MediaReference?
    @FocusState private var focusedFilter: String?

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                CatalogQuickFilters(kind: kind, filters: $filters, focus: $focusedFilter) {
                    showsFilters = true
                }
                ScrollView {
                    MediaPosterGrid(
                        items: model.items.map {
                            .init(
                                reference: .init(kind: kind, id: $0.id), title: $0.displayTitle, poster: $0.posterImage)
                        },
                        isLoading: model.isLoading || (loadedRevision != revision && model.error == nil),
                        onApproachEnd: {
                            guard model.error == nil else { return }
                            Task { await model.load(api: api, kind: kind, filters: filters, more: true) }
                        }, enteringFromMenu: enteringFromMenu || focusedFilter != nil, select: { selectedMedia = $0 })
                    if let error = model.error {
                        FailureView(message: error) {
                            Task {
                                await model.load(api: api, kind: kind, filters: filters, more: !model.items.isEmpty)
                            }
                        }
                    } else if loadedRevision == revision && !model.isLoading && model.items.isEmpty {
                        ContentUnavailableView("No titles found", systemImage: "film")
                    }
                }
                .id(revision)
            }
            .padding(.top, 4)
            .ignoresSafeArea(.container, edges: .horizontal)
            .background(LibraryStyle.background.ignoresSafeArea())
        }
        .task(id: revision) {
            guard loadedRevision != revision else { return }
            let requestedRevision = revision
            await model.load(api: api, kind: kind, filters: filters)
            if !Task.isCancelled { loadedRevision = requestedRevision }
        }
        .modifier(MediaDetailPresentation(reference: $selectedMedia, api: api))
        .onChange(of: filters) { revision += 1 }
        .fullScreenCover(isPresented: $showsFilters) {
            CatalogFilterView(api: api, kind: kind, filters: filters) {
                filters = $0
            }
        }
    }
}
