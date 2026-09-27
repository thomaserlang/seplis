import SwiftUI

struct HomeShelfView: View {
    let model: HomeShelfModel
    let focusedPoster: FocusState<String?>.Binding
    let select: (MediaReference) -> Void

    var body: some View {
        Group {
            if !model.hasLoaded || !model.items.isEmpty || model.error != nil {
                shelfContent
            }
        }
    }

    private var shelfContent: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(model.shelf.title)
                .font(.system(size: 22, weight: .medium))
                .foregroundStyle(.secondary)
                .padding(.horizontal, LibraryStyle.horizontalInset)
            if let error = model.error, model.items.isEmpty {
                FailureView(message: error) { Task { await model.load() } }
            } else if model.items.isEmpty {
                PosterSkeletonRow()
            } else {
                ScrollView(.horizontal) {
                    LazyHStack(spacing: 20) {
                        ForEach(model.items) { item in
                            Button {
                                select(item.reference)
                            } label: {
                                PosterView(
                                    poster: item.media.posterImage, title: item.media.displayTitle,
                                    width: LibraryStyle.posterWidth)
                            }
                            .buttonStyle(PosterButtonStyle())
                            .focusEffectDisabled()
                            .focused(focusedPoster, equals: "\(model.id)-\(item.id)")
                            .accessibilityLabel(item.media.displayTitle)
                            .accessibilityIdentifier("media-\(item.reference.kind.rawValue)-\(item.reference.id)")
                            .id(item.id)
                            .onAppear { Task { await model.loadMoreIfNeeded(near: item.id) } }
                            .onChange(of: focusedPoster.wrappedValue) { _, focus in
                                guard focus == "\(model.id)-\(item.id)" else { return }
                                Task { await model.loadMoreIfNeeded(near: item.id) }
                            }
                        }
                        if model.isLoadingMore {
                            PosterSkeleton()
                        }
                        if let error = model.error {
                            FailureView(message: error) { Task { await model.load(more: true) } }
                        }
                    }
                    .padding(.horizontal, LibraryStyle.horizontalInset)
                    .padding(.top, 10)
                    .padding(.bottom, 10)
                }
                .scrollIndicators(.hidden)
                .scrollClipDisabled()
            }
        }
        .focusSection()
    }
}
