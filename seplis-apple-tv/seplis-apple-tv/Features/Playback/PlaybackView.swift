import SwiftUI

struct PlaybackView: View {
    let api: APIClient
    @State private var model: PlaybackModel
    @Environment(\.dismiss) private var dismiss
    @Environment(\.scenePhase) private var scenePhase
    @State private var isTransitioning = false

    init(target: PlaybackTarget, api: APIClient) {
        self.api = api
        _model = State(initialValue: PlaybackModel(target: target, api: api))
    }

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            NativePlayerView(model: model, close: close, playNext: playNext)
                .id(model.target.id)
                .ignoresSafeArea()
            if let error = model.error {
                VStack(spacing: 24) {
                    FailureView(message: error) { restart(target: model.target) }
                    Button("Back", systemImage: "chevron.backward", action: close)
                }
                .padding(40)
                .background(.regularMaterial)
            } else if model.isLoading {
                Color.black.ignoresSafeArea()
                ProgressView().accessibilityLabel("Preparing video")
            }
            if let error = model.progress?.error {
                VStack {
                    Text(error).font(.caption).padding().background(.regularMaterial)
                    Spacer()
                }
                .padding(60)
            }
        }
        .buttonStyle(LibraryButtonStyle())
        .focusEffectDisabled()
        .alert("Playback preferences", isPresented: Binding(
            get: { model.preferences.error != nil },
            set: { if !$0 { model.preferences.error = nil } }
        )) {
            Button("OK") { model.preferences.error = nil }
        } message: { Text(model.preferences.error ?? "") }
        .task(id: model.target.id) { model.start() }
        .onDisappear {
            let ending = model
            Task { await ending.stop() }
        }
        .onChange(of: scenePhase) { _, phase in
            if phase == .background { close() }
        }
        .onExitCommand { close() }
    }

    private func close() {
        guard !isTransitioning else { return }
        isTransitioning = true
        Task {
            await model.stop()
            dismiss()
        }
    }

    private func playNext() {
        guard let episode = model.nextEpisode else { return }
        restart(target: PlaybackTarget(reference: model.target.reference, title: model.target.title,
                                       episode: episode, fromBeginning: true))
    }

    private func restart(target: PlaybackTarget) {
        guard !isTransitioning else { return }
        isTransitioning = true
        Task {
            await model.stop()
            let fresh = PlaybackTarget(reference: target.reference, title: target.title,
                                       episode: target.episode, fromBeginning: target.fromBeginning)
            model = PlaybackModel(target: fresh, api: api)
            isTransitioning = false
        }
    }
}
