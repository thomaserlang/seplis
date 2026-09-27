import SwiftUI

struct FilterToggleStyle: ToggleStyle {
    func makeBody(configuration: Configuration) -> some View {
        Button { configuration.isOn.toggle() } label: { configuration.label }
            .buttonStyle(FilterButtonStyle(isSelected: configuration.isOn))
            .focusEffectDisabled()
    }
}

struct FilterButtonStyle: ButtonStyle {
    var isSelected = false
    @Environment(\.isFocused) private var isFocused
    @Environment(\.isEnabled) private var isEnabled

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundStyle(.white)
            .padding(.horizontal, 20)
            .frame(minHeight: 60)
            .background(isSelected ? Color(red: 0.16, green: 0.30, blue: 0.44) : LibraryStyle.controlBackground,
                        in: RoundedRectangle(cornerRadius: 8))
            .overlay {
                RoundedRectangle(cornerRadius: 8)
                    .strokeBorder(isFocused ? Color.white : Color.clear, lineWidth: 3)
            }
            .opacity(!isEnabled ? 0.4 : configuration.isPressed ? 0.7 : 1)
    }
}

struct FilterOptionButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                Text(title)
                Spacer()
                Image(systemName: "checkmark").opacity(isSelected ? 1 : 0)
            }
        }
        .buttonStyle(FilterButtonStyle(isSelected: isSelected))
        .focusEffectDisabled()
        .accessibilityLabel(title)
        .accessibilityValue(isSelected ? "Selected" : "Not selected")
    }
}

struct FilterChoiceRow: View {
    let title: String
    @Binding var selection: CatalogChoice
    var inclusionLabels = false

    var body: some View {
        HStack(spacing: 24) {
            Text(title).frame(maxWidth: .infinity, alignment: .leading)
            HStack(spacing: 8) {
                ForEach(CatalogChoice.allCases) { choice in
                    Button { selection = choice } label: {
                        Text(label(choice)).frame(width: 90)
                    }
                    .buttonStyle(FilterButtonStyle(isSelected: selection == choice))
                    .focusEffectDisabled()
                    .accessibilityLabel("\(title): \(label(choice))")
                    .accessibilityValue(selection == choice ? "Selected" : "Not selected")
                }
            }
        }
        .focusSection()
    }

    private func label(_ choice: CatalogChoice) -> String {
        guard inclusionLabels, choice != .any else { return choice.rawValue }
        return choice == .yes ? "Include" : "Exclude"
    }
}
