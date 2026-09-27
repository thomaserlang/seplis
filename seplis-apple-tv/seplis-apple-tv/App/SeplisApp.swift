import SwiftUI

@main
struct SeplisApp: App {
    @State private var session: AppSession

    init() {
        #if DEBUG
        if ProcessInfo.processInfo.arguments.contains("--ui-testing") {
            _session = State(initialValue: UITestFixtures.session())
            return
        }
        #endif
        _session = State(initialValue: AppSession())
    }

    var body: some Scene {
        WindowGroup {
            #if DEBUG
            if ProcessInfo.processInfo.arguments.contains("--ui-testing"),
               ProcessInfo.processInfo.arguments.contains("--playback-info-fixture") {
                PlaybackInfoFixture().ignoresSafeArea()
            } else {
                AppView(session: session)
            }
            #else
            AppView(session: session)
            #endif
        }
    }
}
