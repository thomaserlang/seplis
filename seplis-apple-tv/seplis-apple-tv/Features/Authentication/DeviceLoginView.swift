import SwiftUI

struct DeviceLoginView: View {
    let session: AppSession
    @State private var model: DeviceLoginModel
    @State private var attempt = 0
    @Environment(\.scenePhase) private var scenePhase

    init(session: AppSession) {
        self.session = session
        _model = State(initialValue: DeviceLoginModel(api: session.authorizationAPI))
    }

    var body: some View {
        VStack(spacing: 40) {
            Image("SeplisLogo")
                .resizable()
                .scaledToFit()
                .frame(width: 96, height: 96)
                .clipShape(Circle())
                .accessibilityLabel("SEPLIS")

            if let authorization = model.authorization, !model.expired {
                VStack(spacing: 12) {
                    Text("Go to")
                        .font(.body)
                        .foregroundStyle(.secondary)
                    Text(authorization.verificationUri.formatted(.url.scheme(.never)))
                        .font(.title3.weight(.medium))
                }

                VStack(spacing: 12) {
                    Text("Enter code")
                        .font(.body)
                        .foregroundStyle(.secondary)
                    Text(authorization.userCode)
                        .font(.system(size: 76, weight: .semibold, design: .monospaced))
                        .monospacedDigit()
                        .accessibilityLabel("Sign-in code \(authorization.userCode)")
                }

            } else if model.error == nil {
                ProgressView("Getting a sign-in code")
            }
            if let error = model.error {
                Text(error).foregroundStyle(.secondary).multilineTextAlignment(.center)
                Button(model.expired ? "Get New Code" : "Retry", systemImage: "arrow.clockwise") {
                    attempt += 1
                }
            }
        }
        .multilineTextAlignment(.center)
        .frame(maxWidth: 1200)
        .padding(60)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .task(id: "\(attempt)-\(scenePhase)") {
            if scenePhase == .active { await model.run(session: session) }
        }
    }
}
