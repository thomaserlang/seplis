import SwiftUI

struct AppView: View {
    @Bindable var session: AppSession
    @State private var topShelf = TopShelfPublisher()
    @State private var pendingLink: TopShelfLink?
    @State private var presentedLink: TopShelfLink?
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        Group {
            switch session.state {
            case .restoring:
                ProgressView("Loading profiles")
            case .restoreFailed:
                FailureView(message: "Saved profiles could not be loaded.") { Task { await session.restore() } }
            case .authenticated(let active):
                if let presentedLink {
                    TopShelfDestination(link: presentedLink, api: active.api) { self.presentedLink = nil }
                        .id(presentedLink.id)
                } else {
                    AppTabsView(session: session, api: active.api)
                        .id(active.id)
                }
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
        .task {
            await session.restore()
            if session.api == nil {
                topShelf.configure(api: nil)
                openPendingLink()
            }
        }
        .onChange(of: session.sessionID) {
            if presentedLink?.accountID != session.user?.id { presentedLink = nil }
            topShelf.configure(api: session.api)
            openPendingLink()
        }
        .onChange(of: scenePhase) { _, phase in
            if phase == .active { topShelf.refresh() }
        }
        .onReceive(NotificationCenter.default.publisher(for: .watchHistoryDidChange)) { _ in
            topShelf.refresh()
        }
        .onOpenURL { url in
            pendingLink = TopShelfLink(url: url)
            openPendingLink()
        }
        .alert("Seplis", isPresented: Binding(get: { session.error != nil }, set: { if !$0 { session.error = nil } })) {
            Button("OK") { session.error = nil }
        } message: { Text(session.error ?? "") }
    }

    private func openPendingLink() {
        guard let link = pendingLink else { return }
        if case .restoring = session.state { return }
        pendingLink = nil
        guard session.user?.id == link.accountID else {
            session.error = "Switch to the profile that owns this Continue Watching item, then select it again."
            return
        }
        presentedLink = link
    }
}
