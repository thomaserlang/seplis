import SwiftUI

struct NavigationButtonStyle: ButtonStyle {
    let isSelected: Bool
    @Environment(\.isFocused) private var isFocused

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.horizontal, 24)
            .frame(height: 56)
            .foregroundStyle(isFocused || isSelected ? Color.black : Color.white)
            .background {
                RoundedRectangle(cornerRadius: 8)
                    .fill(isFocused || isSelected ? Color.white : Color.clear)
            }
            .opacity(configuration.isPressed ? 0.8 : 1)
            .animation(nil, value: isFocused)
            .animation(nil, value: isSelected)
    }
}
