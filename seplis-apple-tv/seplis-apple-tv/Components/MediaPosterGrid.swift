import SwiftUI

struct MediaPosterGrid: View {
    struct Item: Identifiable {
        let reference: MediaReference
        let title: String
        let poster: Poster?
        var id: String { "\(reference.kind.rawValue)-\(reference.id)" }
    }
    let items: [Item]
    var isLoading = false
    var onApproachEnd: (() -> Void)?
    var enteringFromMenu = false
    let select: (MediaReference) -> Void
    @FocusState private var focusedID: String?
    @State private var lastFocusedID: String?

    var body: some View {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: LibraryStyle.posterWidth), spacing: 20)], spacing: 20) {
            ForEach(items) { item in
                Button {
                    select(item.reference)
                } label: {
                    PosterView(
                        poster: item.poster, title: item.title,
                        width: LibraryStyle.posterWidth)
                }
                .buttonStyle(PosterButtonStyle())
                .focusEffectDisabled()
                .focused($focusedID, equals: item.id)
                .accessibilityLabel(item.title)
                .accessibilityIdentifier("grid-\(item.id)")
                .id(item.id)
                .onAppear { loadMoreIfNeeded(near: item.id) }
            }
            if isLoading {
                ForEach(0..<18) { _ in
                    PosterSkeleton()
                }
            }
        }
        .padding(.horizontal, LibraryStyle.horizontalInset)
        .padding(.top, 10)
        .padding(.bottom, 12)
        .focusSection()
        .defaultFocus(
            $focusedID, enteringFromMenu ? items.first?.id : lastFocusedID ?? items.first?.id, priority: .userInitiated
        )
        .onChange(of: focusedID) { _, id in
            if let id {
                lastFocusedID = id
                loadMoreIfNeeded(near: id)
            }
        }
    }

    private func loadMoreIfNeeded(near id: String) {
        guard items.suffix(16).contains(where: { $0.id == id }) else { return }
        onApproachEnd?()
    }
}
