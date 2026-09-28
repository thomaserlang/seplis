import SwiftUI

struct MovieCollectionView: View {
    let collection: MovieCollection
    let currentMovieID: Int
    let api: APIClient
    let onOpen: (MediaReference) -> Void
    @State private var model = MovieCollectionModel()
    @FocusState private var focusedMovie: Int?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(collection.name).font(.system(size: 28, weight: .medium)).foregroundStyle(.secondary)
            ScrollView(.horizontal) {
                LazyHStack(spacing: 20) {
                    ForEach(model.movies) { movie in
                        Button {
                            onOpen(MediaReference(kind: .movie, id: movie.id))
                        } label: {
                            PosterView(poster: movie.posterImage, title: movie.displayTitle, width: LibraryStyle.posterWidth)
                        }
                        .buttonStyle(PosterButtonStyle())
                        .focusEffectDisabled()
                        .disabled(movie.id == currentMovieID)
                        .focused($focusedMovie, equals: movie.id)
                        .accessibilityLabel(movie.displayTitle)
                        .accessibilityIdentifier("collection-movie-\(movie.id)")
                        .onAppear {
                            guard model.error == nil, model.movies.suffix(5).contains(where: { $0.id == movie.id }) else { return }
                            Task { await model.load(collectionID: collection.id, api: api, more: true) }
                        }
                    }
                    if model.isLoading || (!model.hasLoaded && model.error == nil) {
                        PosterSkeleton()
                    }
                    if let error = model.error {
                        FailureView(message: error) {
                            Task { await model.load(collectionID: collection.id, api: api, more: model.hasLoaded) }
                        }
                    }
                }
                .padding(4)
            }
            .scrollClipDisabled()
        }
        .focusSection()
        .task { if !model.hasLoaded { await model.load(collectionID: collection.id, api: api) } }
    }
}
