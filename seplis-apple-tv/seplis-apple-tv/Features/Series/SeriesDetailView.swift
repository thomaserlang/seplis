import SwiftUI

struct SeriesDetailView: View {
    let api: APIClient
    var onClose: (() -> Void)?
    @State private var model: SeriesDetailModel
    @State private var playback: PlaybackTarget?
    @Environment(\.dismiss) private var dismiss
    @Namespace private var focusNamespace
    @FocusState private var focusedEpisode: Int?

    init(reference: MediaReference, api: APIClient, onClose: (() -> Void)? = nil) {
        self.api = api
        self.onClose = onClose
        _model = State(initialValue: SeriesDetailModel(reference: reference, api: api))
    }

    var body: some View {
        ScrollView {
            if let series = model.media {
                VStack(alignment: .leading, spacing: 32) {
                    MediaDetailHeader(media: series, actions: seriesActions(series))
                    CastRow(reference: model.reference, api: api)
                    seasons(series)
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
        .defaultFocus($focusedEpisode, preferredEpisodeNumber, priority: .userInitiated)
        .onExitCommand { if let onClose { onClose() } else { dismiss() } }
        .task { await model.load() }
        .fullScreenCover(item: $playback, onDismiss: { Task { await model.load() } }) { target in
            PlaybackView(target: target, api: api)
        }
    }

    private func seriesActions(_ series: Series) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            MediaStateActions(media: series, isUpdating: model.isUpdating,
                              onWatchlist: { Task { await model.toggleWatchlist() } },
                              onFavorite: { Task { await model.toggleFavorite() } })
            episodeActions(series)
        }
    }

    private func episodeActions(_ series: Series) -> some View {
        LazyVGrid(columns: [GridItem(.flexible(), spacing: 24), GridItem(.flexible())],
                  alignment: .leading, spacing: 24) {
            if let episode = model.nextEpisode { episodeActions(episode, series: series, rewatch: false) }
            if let episode = model.lastEpisode { episodeActions(episode, series: series, rewatch: true) }
        }
    }

    private func episodeActions(_ episode: Episode, series: Series, rewatch: Bool) -> some View {
        EpisodeActionsView(heading: rewatch ? "Last watched" : episode.watchHeading, episode: episode,
                           rewatch: rewatch, focusedEpisode: $focusedEpisode, isUpdating: model.isUpdating,
                           play: {
                               playback = PlaybackTarget(reference: model.reference, title: series.displayTitle,
                                                         episode: episode, fromBeginning: rewatch)
                           },
                           increment: { Task { await model.changeWatched(increment: true, episode: episode) } },
                           decrement: { Task { await model.changeWatched(increment: false, episode: episode) } })
    }

    private func seasons(_ series: Series) -> some View {
        VStack(alignment: .leading, spacing: 24) {
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 340), spacing: 24)], spacing: 24) {
                ForEach(series.seasons ?? []) { season in
                    NavigationLink {
                        EpisodesView(reference: model.reference, series: series, season: season.season, api: api)
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
            if series.seasons?.isEmpty != false {
                NavigationLink("All Episodes") {
                    EpisodesView(reference: model.reference, series: series, season: nil, api: api)
                }
            }
        }
    }

    private var preferredEpisodeNumber: Int? {
        if let next = model.nextEpisode, next.canPlay { return next.number }
        if let last = model.lastEpisode, last.canPlay { return last.number }
        return nil
    }
}
