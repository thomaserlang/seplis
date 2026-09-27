import SwiftUI

struct WatchedButton: View {
    let watched: Watched?
    let increment: () -> Void
    let decrement: () -> Void
    @State private var showsAdjustments = false

    private var times: Int { watched?.times ?? 0 }
    private var position: Int { watched?.position ?? 0 }
    var incrementTitle: String { position > 0 || times == 0 ? "Mark as watched" : "Add another watch" }
    var decrementTitle: String { position > 0 ? "Reset watched position" : "Remove last watch" }

    var body: some View {
        MediaStateButton(title: "Watched  \(times)", symbol: "checkmark",
                         isActive: times > 0, color: Color(red: 0.18, green: 0.36, blue: 0.51)) {
            if times == 0 && position == 0 { increment() }
            else { showsAdjustments = true }
        }
        .accessibilityLabel("Watched")
        .accessibilityValue("\(times) times\(position > 0 ? ", in progress" : "")")
        .confirmationDialog("Watched \(times) times", isPresented: $showsAdjustments, titleVisibility: .visible) {
            Button(incrementTitle, systemImage: position > 0 ? "checkmark" : "plus", action: increment)
            Button(decrementTitle, systemImage: position > 0 ? "arrow.counterclockwise" : "minus", action: decrement)
            Button("Cancel", role: .cancel) {}
        } message: {
            if position > 0 {
                Text("Resetting clears the saved playback position without removing completed watches.")
            }
        }
    }
}
