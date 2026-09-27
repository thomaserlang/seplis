import SwiftUI

struct MediaDetailView: View {
    let api: APIClient
    private let onClose: (() -> Void)?
    @State private var model: MediaDetailModel
    @State private var playback: PlaybackTarget?
    @Environment(\.dismiss) private var dismiss
    @Namespace private var focusNamespace
    @FocusState private var focusedEpisode: Int?

    init(reference: MediaReference, api: APIClient, onClose: (() -> Void)? = nil) {
        self.api = api
        self.onClose = onClose
        _model = State(initialValue: MediaDetailModel(reference: reference, api: api))
    }

    var body: some View {
        ScrollView {
            if let media = model.media {
                VStack(alignment: .leading, spacing: 32) {
                    HStack(alignment: .top, spacing: 40) {
                        PosterView(poster: media.posterImage, title: media.displayTitle, width: 240, cornerRadius: 16)
                        VStack(alignment: .leading, spacing: 20) {
                            Text(media.displayTitle).font(.system(size: 42, weight: .semibold))
                            Text(media.metadata).font(.callout).foregroundStyle(.secondary)
                            if let plot = media.plot {
                                Text(plot).font(.system(size: 26)).foregroundStyle(.secondary).lineLimit(5)
                            }
                            if model.reference.kind == .movie {
                                movieActions(media)
                            } else {
                                episodeActions(media)
                            }
                            HStack(spacing: 24) {
                                MediaStateButton(title: "Watchlist", symbol: media.userWatchlist?.onWatchlist == true ? "bookmark.fill" : "bookmark",
                                                 isActive: media.userWatchlist?.onWatchlist == true,
                                                 color: .indigo) { Task { await model.toggleWatchlist() } }
                                MediaStateButton(title: "Favorite", symbol: media.userFavorite?.favorite == true ? "star.fill" : "star",
                                                 isActive: media.userFavorite?.favorite == true,
                                                 color: Color(red: 0.65, green: 0.29, blue: 0.02)) {
                                    Task { await model.toggleFavorite() }
                                }
                            }
                            .disabled(model.isUpdating)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    if model.reference.kind == .movie, let collection = media.collection {
                        MovieCollectionView(collection: collection, currentMovieID: media.id, api: api)
                            .id(collection.id)
                    }
                    if model.reference.kind == .series {
                        Text("Seasons").font(.system(size: 28, weight: .medium)).foregroundStyle(.secondary)
                        LazyVGrid(columns: [GridItem(.adaptive(minimum: 340), spacing: 24)], spacing: 24) {
                            ForEach(media.seasons ?? []) { season in
                                NavigationLink {
                                    EpisodesView(reference: model.reference, media: media, season: season.season, api: api)
                                } label: {
                                    VStack(alignment: .leading, spacing: 6) {
                                        Text("Season \(season.season)").font(.body)
                                        Text("\(season.total) episodes").font(.caption).foregroundStyle(.secondary)
                                    }
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                }
                            }
                        }
                        .focusSection()
                        if media.seasons?.isEmpty != false {
                            NavigationLink("All Episodes") {
                                EpisodesView(reference: model.reference, media: media, season: nil, api: api)
                            }
                        }
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
                ProgressView("Loading title")
                    .padding(64)
                    .focusable()
                    .accessibilityIdentifier("media-detail-loading")
            }
        }
        .background(LibraryStyle.background.ignoresSafeArea())
        .buttonStyle(LibraryButtonStyle())
        .focusEffectDisabled()
        .focusScope(focusNamespace)
        .defaultFocus($focusedEpisode, preferredEpisodeNumber, priority: .userInitiated)
        .onExitCommand {
            if let onClose { onClose() } else { dismiss() }
        }
        .task { await model.load() }
        .fullScreenCover(item: $playback, onDismiss: { Task { await model.load() } }) { target in
            PlaybackView(target: target, api: api)
        }
    }

    private func movieActions(_ media: Media) -> some View {
        HStack(spacing: 24) {
            Button((media.userWatched?.position ?? 0) > 0 ? "Resume" : "Play", systemImage: model.canPlayMovie ? "play.fill" : "play") {
                play(media: media)
            }
            .disabled(!model.canPlayMovie)
            .prefersDefaultFocus(model.canPlayMovie, in: focusNamespace)
            WatchedButton(watched: media.userWatched,
                          increment: { Task { await model.changeWatched(increment: true) } },
                          decrement: { Task { await model.changeWatched(increment: false) } })
            .disabled(model.isUpdating)
        }
    }

    private func episodeActions(_ media: Media) -> some View {
        LazyVGrid(columns: [GridItem(.flexible(), spacing: 24), GridItem(.flexible())], alignment: .leading, spacing: 24) {
            if let episode = model.nextEpisode {
                episodeActions(episode, media: media, rewatch: false)
            }
            if let episode = model.lastEpisode {
                episodeActions(episode, media: media, rewatch: true)
            }
        }
    }

    private func episodeActions(_ episode: Episode, media: Media, rewatch: Bool) -> some View {
        EpisodeActionsView(heading: rewatch ? "Last watched" : episode.watchHeading, episode: episode,
                           rewatch: rewatch, focusedEpisode: $focusedEpisode,
                           isUpdating: model.isUpdating,
                           play: { play(media: media, episode: episode, restart: rewatch) },
                           increment: { Task { await model.changeWatched(increment: true, episode: episode) } },
                           decrement: { Task { await model.changeWatched(increment: false, episode: episode) } })
    }

    private func play(media: Media, episode: Episode? = nil, restart: Bool = false) {
        playback = PlaybackTarget(reference: model.reference, title: media.displayTitle,
                                  episode: episode, fromBeginning: restart)
    }

    private var preferredEpisodeNumber: Int? {
        if let next = model.nextEpisode, next.canPlay { return next.number }
        if let last = model.lastEpisode, last.canPlay { return last.number }
        return nil
    }
}
