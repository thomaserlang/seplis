import SwiftUI

struct SeasonEpisodeRow: View {
    let episode: Episode
    let playAction: PlaybackAction
    let isUpdating: Bool
    let play: () -> Void
    let increment: () -> Void
    let decrement: () -> Void

    private var title: String { episode.title ?? "Episode \(episode.episode ?? episode.number)" }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 14) {
                Text(episode.numberLabel)
                    .font(.system(size: 22, weight: .semibold))
                    .foregroundStyle(Color(red: 0.55, green: 0.73, blue: 0.91))
                if let airDate = episode.airDate {
                    Text(airDate)
                        .font(.system(size: 19))
                        .foregroundStyle(.secondary)
                }
                Spacer(minLength: 8)
                if let runtime = episode.runtime {
                    Text("\(runtime) min")
                        .font(.system(size: 19))
                        .foregroundStyle(.secondary)
                }
            }
            Text(title)
                .font(.system(size: 25, weight: .semibold))
                .lineLimit(1)
                .frame(maxWidth: .infinity, alignment: .leading)
            if let plot = episode.plot, !plot.isEmpty {
                Text(plot)
                    .font(.system(size: 20))
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
            HStack(spacing: 12) {
                Button(playAction.title, systemImage: playAction.systemImage, action: play)
                    .disabled(!episode.canPlay)
                    .accessibilityLabel("\(playAction.title) \(episode.label)")
                WatchedButton(watched: episode.userWatched, durationMinutes: episode.runtime,
                              increment: increment, decrement: decrement)
                    .disabled(isUpdating)
                    .accessibilityIdentifier("episode-watched-\(episode.number)")
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(white: 0.045), in: RoundedRectangle(cornerRadius: 8))
        .overlay {
            RoundedRectangle(cornerRadius: 8).strokeBorder(Color(white: 0.16), lineWidth: 1)
        }
        .focusSection()
    }
}
