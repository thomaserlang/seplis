import SwiftUI

struct MovieDetailView: View {
    let api: APIClient
    var onClose: (() -> Void)?
    @State private var model: MovieDetailModel
    @State private var playback: PlaybackTarget?
    @Environment(\.dismiss) private var dismiss
    @Namespace private var focusNamespace

    init(reference: MediaReference, api: APIClient, onClose: (() -> Void)? = nil) {
        self.api = api
        self.onClose = onClose
        _model = State(initialValue: MovieDetailModel(reference: reference, api: api))
    }

    var body: some View {
        ScrollView {
            if let movie = model.media {
                VStack(alignment: .leading, spacing: 32) {
                    MediaDetailHeader(media: movie, actions: movieActions(movie))
                    if let collection = movie.collection {
                        MovieCollectionView(collection: collection, currentMovieID: movie.id, api: api)
                            .id(collection.id)
                    }
                    if let error = model.error {
                        FailureView(message: error) { Task { await model.load() } }
                    }
                }
                .padding(.horizontal, LibraryStyle.horizontalInset)
                .padding(.vertical, 32)
            } else if let error = model.error {
                FailureView(message: error) { Task { await model.load() } }
            } else {
                ProgressView("Loading title").padding(64).focusable()
                    .accessibilityIdentifier("media-detail-loading")
            }
        }
        .background(LibraryStyle.background.ignoresSafeArea())
        .buttonStyle(LibraryButtonStyle())
        .focusEffectDisabled()
        .focusScope(focusNamespace)
        .onExitCommand { if let onClose { onClose() } else { dismiss() } }
        .task { await model.load() }
        .fullScreenCover(item: $playback, onDismiss: { Task { await model.load() } }) { target in
            PlaybackView(target: target, api: api)
        }
    }

    private func movieActions(_ movie: Movie) -> some View {
        HStack(spacing: 24) {
            Button((movie.userWatched?.position ?? 0) > 0 ? "Resume" : "Play",
                   systemImage: model.canPlay ? "play.fill" : "play") {
                playback = PlaybackTarget(reference: model.reference, title: movie.displayTitle,
                                          episode: nil, fromBeginning: false)
            }
            .disabled(!model.canPlay)
            .prefersDefaultFocus(model.canPlay, in: focusNamespace)
            WatchedButton(watched: movie.userWatched,
                          increment: { Task { await model.changeWatched(increment: true) } },
                          decrement: { Task { await model.changeWatched(increment: false) } })
                .disabled(model.isUpdating)
            MediaStateActions(media: movie, isUpdating: model.isUpdating,
                              onWatchlist: { Task { await model.toggleWatchlist() } },
                              onFavorite: { Task { await model.toggleFavorite() } })
        }
    }
}
