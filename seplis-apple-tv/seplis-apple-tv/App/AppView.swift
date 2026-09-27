import SwiftUI

struct AppView: View {
    @Bindable var session: AppSession

    var body: some View {
        Group {
            switch session.state {
            case .restoring:
                ProgressView("Loading profiles")
            case .restoreFailed:
                FailureView(message: "Saved profiles could not be loaded.") { Task { await session.restore() } }
            case .authenticated(let active):
                AppTabsView(session: session, api: active.api)
                    .id(active.id)
            case .choosingProfile:
                ProfilesView(session: session)
            case .signedOut:
                DeviceLoginView(session: session)
            }
        }
        .background(LibraryStyle.background.ignoresSafeArea())
        .preferredColorScheme(.dark)
        .buttonBorderShape(.roundedRectangle(radius: 8))
        .buttonStyle(LibraryButtonStyle())
        .focusEffectDisabled()
        .task { await session.restore() }
        .alert("Seplis", isPresented: Binding(get: { session.error != nil }, set: { if !$0 { session.error = nil } })) {
            Button("OK") { session.error = nil }
        } message: { Text(session.error ?? "") }
    }
}
