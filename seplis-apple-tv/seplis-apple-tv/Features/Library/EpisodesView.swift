import SwiftUI

struct EpisodesView: View {
    let reference: MediaReference
    let media: Media
    let season: Int?
    let api: APIClient
    @State private var model = EpisodesModel()
    @State private var playback: PlaybackTarget?
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        Group {
            if let error = model.error {
                FailureView(message: error) { Task { await load() } }
            } else if model.isLoading && model.episodes.isEmpty {
                ProgressView("Loading episodes")
            } else {
                ScrollView {
                    LazyVStack(spacing: 16) {
                        ForEach(model.episodes) { episode in
                            episodeRow(episode)
                        }
                    }
                    .padding(.horizontal, LibraryStyle.horizontalInset)
                    .padding(.vertical, 16)
                }
                .overlay { if model.episodes.isEmpty { Text("No episodes available") } }
            }
        }
        .background(LibraryStyle.background.ignoresSafeArea())
        .buttonStyle(LibraryButtonStyle())
        .focusEffectDisabled()
        .navigationTitle(season.map { "Season \($0)" } ?? "Episodes")
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

    private func episodeRow(_ episode: Episode) -> some View {
        HStack(spacing: 20) {
            Button {
                playback = PlaybackTarget(reference: reference, title: media.displayTitle,
                                          episode: episode, fromBeginning: true)
            } label: {
                HStack {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(episode.label)
                        if let date = episode.airDate {
                            Text(date).font(.caption).foregroundStyle(.secondary)
                        }
                    }
                    Spacer()
                    if !episode.canPlay {
                        Text("Unavailable").foregroundStyle(.secondary)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .disabled(!episode.canPlay)
            WatchedButton(watched: episode.userWatched,
                          increment: { changeWatched(episode, increment: true) },
                          decrement: { changeWatched(episode, increment: false) })
                .disabled(model.isUpdating)
                .accessibilityIdentifier("episode-watched-\(episode.number)")
        }
        .focusSection()
    }

    private func changeWatched(_ episode: Episode, increment: Bool) {
        Task { await model.changeWatched(reference: reference, episode: episode,
                                         increment: increment, season: season, api: api) }
    }

    private func load() async { await model.load(reference: reference, season: season, api: api) }
}
