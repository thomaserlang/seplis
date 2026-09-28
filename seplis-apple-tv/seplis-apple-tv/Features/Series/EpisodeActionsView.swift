import SwiftUI

struct EpisodeActionsView: View {
    let heading: String
    let episode: Episode
    let rewatch: Bool
    let focusedEpisode: FocusState<Int?>.Binding
    let isUpdating: Bool
    let play: () -> Void
    let increment: () -> Void
    let decrement: () -> Void

    private var playTitle: String {
        if rewatch { return "Rewatch" }
        return (episode.userWatched?.position ?? 0) > 0 ? "Resume" : "Play"
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(heading).font(.system(size: 20, weight: .medium)).foregroundStyle(.secondary)
            VStack(alignment: .leading, spacing: 14) {
                HStack(spacing: 14) {
                    Text(episode.numberLabel).font(.system(size: 22, weight: .semibold))
                        .foregroundStyle(Color(red: 0.55, green: 0.73, blue: 0.91))
                    if let date = episode.airDate {
                        Text(date).font(.system(size: 22)).foregroundStyle(.secondary)
                    }
                }
                Text(episode.title ?? "").font(.system(size: 24, weight: .medium)).lineLimit(1)
                HStack(spacing: 12) {
                    Button(playTitle, systemImage: rewatch ? "arrow.counterclockwise" : "play.fill", action: play)
                        .disabled(!episode.canPlay)
                        .focused(focusedEpisode, equals: episode.number)
                        .accessibilityLabel("\(playTitle) \(episode.numberLabel)")
                    WatchedButton(watched: episode.userWatched, durationMinutes: episode.runtime,
                                  increment: increment, decrement: decrement)
                        .disabled(isUpdating)
                        .accessibilityIdentifier("episode-watched-\(episode.number)")
                }
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .overlay {
                RoundedRectangle(cornerRadius: 8).strokeBorder(Color(white: 0.14), lineWidth: 1)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .focusSection()
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("episode-actions-\(episode.number)")
    }
}
