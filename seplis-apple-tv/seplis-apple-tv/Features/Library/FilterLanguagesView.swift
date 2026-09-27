import SwiftUI

struct FilterLanguagesView: View {
    @Binding var selection: Set<String>
    private let languages = Locale.LanguageCode.isoLanguageCodes.map(\.identifier).filter { $0.count == 2 }
        .map { (Locale.current.localizedString(forLanguageCode: $0) ?? $0, $0) }.sorted { $0.0 < $1.0 }

    var body: some View {
        LazyVStack(spacing: 12) {
            ForEach(languages, id: \.1) { name, code in
                Toggle(isOn: Binding(get: { selection.contains(code) }, set: {
                    if $0 { selection.insert(code) } else { selection.remove(code) }
                })) {
                    HStack {
                        Text(name)
                        Spacer()
                        Image(systemName: selection.contains(code) ? "checkmark.square" : "square")
                    }
                }
                .toggleStyle(FilterToggleStyle())
            }
        }
    }
}
