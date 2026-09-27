import SwiftUI

struct FailureView: View {
    let message: String
    let retry: () -> Void

    var body: some View {
        VStack(spacing: 24) {
            Text(message).foregroundStyle(.secondary).multilineTextAlignment(.center)
            Button("Retry", systemImage: "arrow.clockwise", action: retry)
        }
        .padding()
    }
}
