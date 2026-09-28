import SwiftUI

struct TopShelfDestination: View {
    let link: TopShelfLink
    let api: APIClient
    let close: () -> Void
    @State private var target: PlaybackTarget?
    @State private var error: String?

    private var reference: MediaReference {
        MediaReference(kind: link.kind == "series" ? .series : .movie, id: link.mediaID)
    }

    var body: some View {
        Group {
            if !link.play {
                NavigationStack {
                    MediaDetailView(reference: reference, api: api, onClose: close)
                        .navigationDestination(for: MediaReference.self) { reference in
                            MediaDetailView(reference: reference, api: api)
                        }
                }
            } else if let target {
                PlaybackView(target: target, api: api, onClose: close)
            } else if let error {
                FailureView(message: error) { Task { await load() } }
                    .onExitCommand(perform: close)
            } else {
                ProgressView("Preparing video")
                    .onExitCommand(perform: close)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(.black)
        .task { if link.play { await load() } }
    }

    private func load() async {
        error = nil
        do {
            let media: MediaSummary = try await api.get(reference.path)
            let episode: Episode?
            if let number = link.episodeNumber, reference.kind == .series {
                episode = try await api.get("\(reference.path)/episodes/\(number)")
            } else {
                episode = nil
            }
            try Task.checkCancellation()
            target = PlaybackTarget(reference: reference, title: media.displayTitle,
                                    episode: episode, fromBeginning: false)
        } catch is CancellationError {
        } catch { self.error = error.localizedDescription }
    }
}
