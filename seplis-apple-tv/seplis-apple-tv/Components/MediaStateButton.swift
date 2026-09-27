import SwiftUI

struct MediaStateButton: View {
    let title: String
    let symbol: String
    let isActive: Bool
    let color: Color
    let action: () -> Void

    var body: some View {
        Button(title, systemImage: symbol, action: action)
            .buttonStyle(LibraryButtonStyle(background: isActive ? color : LibraryStyle.controlBackground))
            .focusEffectDisabled()
            .accessibilityValue(isActive ? "On" : "Off")
    }
}
