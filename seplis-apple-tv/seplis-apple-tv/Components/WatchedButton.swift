import SwiftUI

struct WatchedButton: View {
    let watched: Watched?
    let durationMinutes: Int?
    let increment: () -> Void
    let decrement: () -> Void
    @State private var showsAdjustments = false

    private var times: Int { watched?.times ?? 0 }
    private var position: Int { watched?.position ?? 0 }
    var progress: CGFloat {
        guard position > 0 else { return 0 }
        guard let durationMinutes, durationMinutes > 0 else { return 0.5 }
        return min(1, max(0.15, CGFloat(position) / CGFloat(durationMinutes * 60)))
    }
    var incrementTitle: String { position > 0 || times == 0 ? "Mark as watched" : "Add another watch" }
    var decrementTitle: String { position > 0 ? "Reset watched position" : "Remove last watch" }

    var body: some View {
        Button {
            if times == 0 && position == 0 { increment() }
            else { showsAdjustments = true }
        } label: {
            HStack(spacing: 0) {
                HStack(spacing: 10) {
                    Image(systemName: times > 0 ? "checkmark.square.fill" : "checkmark")
                    Text("Watched")
                }
                .padding(.horizontal, 16)
                .frame(height: 62)
                .background(times > 0 ? Color(red: 0.18, green: 0.36, blue: 0.51) : LibraryStyle.controlBackground)
                .overlay(alignment: .bottomLeading) {
                    GeometryReader { geometry in
                        Rectangle()
                            .fill(Color(red: 0.42, green: 0.67, blue: 0.84))
                            .frame(width: geometry.size.width * progress, height: 4)
                            .frame(maxHeight: .infinity, alignment: .bottom)
                    }
                }
                Rectangle().fill(Color.white.opacity(0.15)).frame(width: 1)
                Text("\(times)")
                    .monospacedDigit()
                    .frame(width: 52, height: 62)
                    .background(LibraryStyle.controlBackground)
            }
            .font(.system(size: 24, weight: .medium))
            .foregroundStyle(.white)
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
        .buttonStyle(WatchedButtonStyle())
        .focusEffectDisabled()
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

private struct WatchedButtonStyle: ButtonStyle {
    @Environment(\.isFocused) private var isFocused
    @Environment(\.isEnabled) private var isEnabled

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .overlay {
                RoundedRectangle(cornerRadius: 8)
                    .strokeBorder(isFocused ? .white : .clear, lineWidth: 3)
            }
            .opacity(!isEnabled ? 0.4 : configuration.isPressed ? 0.75 : 1)
    }
}
