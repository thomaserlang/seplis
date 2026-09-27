import SwiftUI

struct CatalogQuickFilters: View {
    let kind: MediaKind
    @Binding var filters: CatalogFilters
    var focus: FocusState<String?>.Binding
    let showSettings: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Button("Filters", systemImage: "line.3.horizontal.decrease", action: showSettings)
                .buttonStyle(FilterButtonStyle())
                .focused(focus, equals: "settings")
                .accessibilityIdentifier("\(kind.rawValue)-filters")
            quickToggle("Available", id: "available", choice: $filters.available)
            quickSort("New", id: "new", value: kind == .movie ? "release_date_desc" : "premiered_desc")
            quickSort("Popular", id: "popular", value: "popularity_desc")
            quickToggle("Not Watched", id: "unwatched", choice: $filters.watched, active: .no)
            quickToggle("Watchlist", id: "watchlist", choice: $filters.watchlist)
            quickToggle("Favorites", id: "favorites", choice: $filters.favorite)
            Spacer(minLength: 0)
        }
        .font(.body)
        .focusEffectDisabled()
        .padding(.horizontal, LibraryStyle.horizontalInset)
        .padding(.bottom, 4)
        .focusSection()
        .defaultFocus(focus, "settings", priority: .userInitiated)
    }

    private func quickSort(_ title: String, id: String, value: String) -> some View {
        Button(title) { filters.sort = value }
            .buttonStyle(FilterButtonStyle(isSelected: filters.sort == value))
            .focused(focus, equals: id)
            .accessibilityValue(filters.sort == value ? "Selected" : "Not selected")
            .accessibilityIdentifier("\(kind.rawValue)-quick-\(id)")
    }

    private func quickToggle(
        _ title: String, id: String, choice: Binding<CatalogChoice>, active: CatalogChoice = .yes
    ) -> some View {
        Toggle(title, isOn: Binding(
            get: { choice.wrappedValue == active },
            set: { choice.wrappedValue = $0 ? active : .any }
        ))
        .toggleStyle(FilterToggleStyle())
        .focused(focus, equals: id)
        .accessibilityIdentifier("\(kind.rawValue)-quick-\(id)")
    }
}
