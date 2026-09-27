import SwiftUI

struct PosterButtonStyle: ButtonStyle {
    @Environment(\.isFocused) private var isFocused
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .overlay {
                RoundedRectangle(cornerRadius: 8)
                    .strokeBorder(isFocused ? Color.white : Color.clear, lineWidth: 4)
                    .allowsHitTesting(false)
            }
            .opacity(configuration.isPressed ? 0.8 : 1)
            .scaleEffect(isFocused ? 1.06 : 1)
            .animation(.easeOut(duration: 0.15), value: isFocused)
    }
}
