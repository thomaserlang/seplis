import SwiftUI

struct EpisodesView: View {
    let reference: MediaReference
    let series: Series
    let season: Int?
    let api: APIClient
    @State private var model = EpisodesModel()
    @State private var playback: PlaybackTarget?
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        MediaDetailLayout(poster: series.posterImage, headerSpacing: 0) {
            EmptyView()
        } content: {
            if let error = model.error {
                FailureView(message: error) { Task { await load() } }
            } else if model.isLoading && model.episodes.isEmpty {
                ProgressView("Loading episodes")
            } else {
                LazyVStack(spacing: 16) {
                    ForEach(model.episodes) { episode in
                        let playAction = PlaybackAction(watched: episode.userWatched, rewatchCompleted: true)
                        SeasonEpisodeRow(episode: episode, playAction: playAction, isUpdating: model.isUpdating,
                                         play: {
                                             playback = PlaybackTarget(reference: reference, title: series.displayTitle,
                                                                       episode: episode, fromBeginning: playAction.fromBeginning)
                                         },
                                         increment: { changeWatched(episode, increment: true) },
                                         decrement: { changeWatched(episode, increment: false) })
                    }
                }
                .overlay { if model.episodes.isEmpty { Text("No episodes available") } }
            }
        }
        .buttonStyle(LibraryButtonStyle())
        .focusEffectDisabled()
        .onExitCommand { dismiss() }
        .task { await load() }
        .fullScreenCover(item: $playback, onDismiss: { Task { await load() } }) { target in
            PlaybackView(target: target, api: api)
        }
        .alert("Could not update watched count", isPresented: Binding(
            get: { model.updateError != nil }, set: { if !$0 { model.updateError = nil } }
        )) {
            Button("OK") { model.updateError = nil }
        } message: { Text(model.updateError ?? "") }
    }

    private func changeWatched(_ episode: Episode, increment: Bool) {
        Task { await model.changeWatched(reference: reference, episode: episode,
                                         increment: increment, season: season, api: api) }
    }

    private func load() async { await model.load(reference: reference, season: season, api: api) }
}
