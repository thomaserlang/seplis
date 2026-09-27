import SwiftUI

struct FilterRangeView: View {
    let title: String
    @Binding var minimum: String
    @Binding var maximum: String

    var body: some View {
        HStack(alignment: .top, spacing: 32) {
            field("Minimum", text: $minimum)
            field("Maximum", text: $maximum)
        }
    }

    private func field(_ label: String, text: Binding<String>) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(label).foregroundStyle(.secondary)
            FilterNumberField(label: "\(title) \(label.lowercased())", text: text)
            Button("Clear \(label.lowercased())", systemImage: "xmark") { text.wrappedValue = "" }
                .buttonStyle(FilterButtonStyle())
                .focusEffectDisabled()
                .disabled(text.wrappedValue.isEmpty)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct FilterNumberField: View {
    let label: String
    @Binding var text: String
    @FocusState private var isFocused: Bool

    var body: some View {
        TextField("Any", text: $text, prompt: Text("Any").foregroundStyle(Color.white.opacity(0.65)))
            .textFieldStyle(.plain)
            .foregroundStyle(.white)
            .keyboardType(.decimalPad)
            .padding(.horizontal, 20)
            .frame(height: 60)
            .background(LibraryStyle.controlBackground, in: RoundedRectangle(cornerRadius: 8))
            .overlay {
                RoundedRectangle(cornerRadius: 8)
                    .strokeBorder(isFocused ? Color.white : Color.clear, lineWidth: 3)
            }
            .focused($isFocused)
            .focusEffectDisabled()
            .accessibilityLabel(label)
    }
}
