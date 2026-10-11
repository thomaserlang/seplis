import SwiftUI

struct DeviceLoginView: View {
    let session: AppSession
    let showsLogo: Bool
    @State private var model: DeviceLoginModel
    @State private var attempt = 0
    @Environment(\.scenePhase) private var scenePhase

    init(session: AppSession, showsLogo: Bool = false) {
        self.session = session
        self.showsLogo = showsLogo
        _model = State(initialValue: DeviceLoginModel(api: session.authorizationAPI))
    }

    var body: some View {
        Group {
            if showsLogo {
                VStack(spacing: 40) {
                    Image("SeplisLogo")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 128, height: 128)
                        .clipShape(Circle())
                        .accessibilityLabel("SEPLIS")
                    form
                        .background(Color(white: 0.067), in: RoundedRectangle(cornerRadius: 32))
                        .overlay {
                            RoundedRectangle(cornerRadius: 32)
                                .strokeBorder(.white.opacity(0.08), lineWidth: 1)
                        }
                }
                .padding(60)
                .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
                .background(Color.black.ignoresSafeArea())
            } else {
                form
            }
        }
        .presentationSizing(.fitted)
        .task(id: "\(attempt)-\(scenePhase)") {
            if scenePhase == .active { await model.run(session: session) }
        }
    }

    private var form: some View {
        VStack(spacing: 40) {
            Text("Sign in to SEPLIS")
                .font(.system(size: 48, weight: .semibold))
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)

            if let authorization = model.authorization, !model.expired {
                HStack(alignment: .top, spacing: 64) {
                    QRCodeView(url: authorization.verificationUriComplete.absoluteString)
                        .frame(width: 300, height: 300)
                    VStack(alignment: .leading, spacing: 0) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Go to")
                                .font(.body)
                                .foregroundStyle(.secondary)
                            Text(authorization.verificationUri.formatted(.url.scheme(.never)))
                                .font(.title3.weight(.medium))
                        }
                        Spacer(minLength: 28)
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Enter code")
                                .font(.body)
                                .foregroundStyle(.secondary)
                            Text(authorization.userCode)
                                .font(.system(size: 96, weight: .bold, design: .monospaced))
                                .foregroundStyle(.white)
                                .monospacedDigit()
                                .lineLimit(1)
                                .minimumScaleFactor(0.5)
                                .accessibilityLabel("Sign-in code \(authorization.userCode)")
                        }
                    }
                    .multilineTextAlignment(.leading)
                    .frame(maxWidth: 400, alignment: .leading)
                    .frame(height: 300)
                }
            } else if model.error == nil {
                ProgressView()
                    .accessibilityLabel("Getting a sign-in code")
                    .frame(height: 300)
            }
            if let error = model.error {
                Text(error).foregroundStyle(.secondary).multilineTextAlignment(.center)
                Button(model.expired ? "Get New Code" : "Retry", systemImage: "arrow.clockwise") {
                    attempt += 1
                }
            }
        }
        .multilineTextAlignment(.center)
        .frame(maxWidth: 764)
        .padding(.horizontal, 60)
        .padding(.top, 40)
        .padding(.bottom, 60)
    }
}
