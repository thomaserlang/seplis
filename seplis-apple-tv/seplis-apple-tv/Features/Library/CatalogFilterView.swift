import SwiftUI

struct CatalogFilterView: View {
    let api: APIClient
    let kind: MediaKind
    @State var filters: CatalogFilters
    let apply: (CatalogFilters) -> Void
    @State private var category: Category = .sort
    @State private var genres: [CatalogGenre] = []
    @State private var genreError: String?
    @State private var loadingGenres = true
    @Environment(\.dismiss) private var dismiss

    private enum Category: String, CaseIterable {
        case sort = "Sort", library = "Library", genres = "Genres", languages = "Languages"
        case year = "Year", rating = "IMDb Rating", votes = "IMDb Votes"
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 32) {
            HStack(spacing: 20) {
                Text("Filters").font(.system(size: 36, weight: .semibold))
                Spacer()
                Button("Reset Filters", systemImage: "arrow.counterclockwise") { filters = CatalogFilters() }
                Button("Apply Filters", systemImage: "checkmark") { apply(filters); dismiss() }
                    .disabled(filters.validationError != nil)
                Button("Cancel", systemImage: "xmark") { dismiss() }.labelStyle(.iconOnly)
            }
            .buttonStyle(FilterButtonStyle())
            .focusEffectDisabled()
            .focusSection()

            HStack(alignment: .top, spacing: 56) {
                VStack(spacing: 12) {
                    ForEach(Category.allCases, id: \.self) { item in
                        Button { category = item } label: {
                            HStack {
                                Text(item.rawValue)
                                Spacer()
                                Image(systemName: "chevron.right").font(.system(size: 18))
                            }
                        }
                        .buttonStyle(FilterButtonStyle(isSelected: category == item))
                        .focusEffectDisabled()
                        .accessibilityIdentifier("filter-category-\(item.rawValue)")
                        .accessibilityAddTraits(category == item ? .isSelected : [])
                    }
                    Spacer(minLength: 0)
                }
                .frame(width: 310)
                .focusSection()

                ScrollView {
                    VStack(alignment: .leading, spacing: 24) {
                        Text(category.rawValue).font(.system(size: 28, weight: .semibold))
                        options
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(6)
                }
                .id(category)
                .focusSection()
            }
            if let error = filters.validationError { Text(error).foregroundStyle(.red) }
        }
        .font(.system(size: 24))
        .padding(.horizontal, 64)
        .padding(.vertical, 40)
        .background(LibraryStyle.background.ignoresSafeArea())
        .onExitCommand { dismiss() }
        .task { await loadGenres() }
    }

    @ViewBuilder private var options: some View {
        switch category {
        case .sort:
            ForEach(CatalogFilters.sorts(for: kind), id: \.1) { title, value in
                FilterOptionButton(title: title, isSelected: filters.sort == value) { filters.sort = value }
            }
        case .library:
            FilterChoiceRow(title: "Available to play", selection: $filters.available)
            FilterChoiceRow(title: "On watchlist", selection: $filters.watchlist)
            FilterChoiceRow(title: "Favorite", selection: $filters.favorite)
            FilterChoiceRow(title: "Watched", selection: $filters.watched)
        case .genres:
            if loadingGenres { ProgressView() }
            ForEach(genres) { genre in
                FilterChoiceRow(title: genre.name, selection: Binding(
                    get: { filters.genres[genre.id] ?? .any },
                    set: { filters.genres[genre.id] = $0 }
                ), inclusionLabels: true)
            }
            if let genreError { FailureView(message: genreError) { Task { await loadGenres() } } }
        case .languages:
            FilterLanguagesView(selection: $filters.languages)
        case .year:
            FilterRangeView(title: "Year", minimum: $filters.yearFrom, maximum: $filters.yearTo)
        case .rating:
            FilterRangeView(title: "IMDb rating", minimum: $filters.ratingFrom, maximum: $filters.ratingTo)
        case .votes:
            FilterRangeView(title: "IMDb votes", minimum: $filters.votesFrom, maximum: $filters.votesTo)
        }
    }

    private func loadGenres() async {
        loadingGenres = true
        defer { loadingGenres = false }
        do {
            genres = try await api.get("genres", query: [.init(name: "type", value: kind.rawValue)])
            genreError = nil
        } catch { genreError = error.localizedDescription }
    }
}
