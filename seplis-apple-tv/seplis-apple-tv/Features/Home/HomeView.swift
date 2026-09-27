import SwiftUI

struct HomeView: View {
    let api: APIClient
    let enteringFromMenu: Bool
    let autoFocusOnLoad: Bool
    let isActive: Bool
    @State private var shelves: [HomeShelfModel]
    @State private var selectedMedia: MediaReference?
    @FocusState private var focusedPoster: String?
    @State private var didSetInitialFocus = false
    @State private var lastFocusedID: String?

    init(api: APIClient, enteringFromMenu: Bool, autoFocusOnLoad: Bool, isActive: Bool) {
        self.api = api
        self.enteringFromMenu = enteringFromMenu
        self.autoFocusOnLoad = autoFocusOnLoad
        self.isActive = isActive
        _shelves = State(initialValue: HomeShelf.allCases.map { HomeShelfModel(shelf: $0, api: api) })
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 4) {
                    ForEach(shelves) { shelf in
                        HomeShelfView(
                            model: shelf, focusedPoster: $focusedPoster
                        ) { selectedMedia = $0 }
                        .id(shelf.id)
                    }
                }
                .padding(.top, 4)
                .padding(.bottom, 40)
            }
            .ignoresSafeArea(.container, edges: .horizontal)
            .background(LibraryStyle.background.ignoresSafeArea())
            .defaultFocus(
                $focusedPoster, enteringFromMenu ? initialPosterID : lastFocusedID ?? initialPosterID,
                priority: .userInitiated)
        }
        .modifier(MediaDetailPresentation(reference: $selectedMedia, api: api))
        .task(id: isActive && selectedMedia == nil) {
            guard isActive, selectedMedia == nil else { return }
            await withTaskGroup(of: Void.self) { group in
                for shelf in shelves { group.addTask { await shelf.load() } }
            }
        }
        .onChange(of: initialPosterID) { _, id in
            guard isActive, selectedMedia == nil, !didSetInitialFocus, autoFocusOnLoad, let id else { return }
            didSetInitialFocus = true
            focusedPoster = id
        }
        .onChange(of: focusedPoster) { _, id in
            if let id { lastFocusedID = id }
        }
    }

    private var initialPosterID: String? {
        for shelf in shelves {
            if let first = shelf.items.first { return "\(shelf.id)-\(first.id)" }
            if !shelf.hasLoaded && shelf.error == nil { return nil }
        }
        return nil
    }

}
