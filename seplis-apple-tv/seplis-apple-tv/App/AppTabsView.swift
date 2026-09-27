import SwiftUI

struct AppTabsView: View {
    let session: AppSession
    let api: APIClient
    @State private var section: Section = .home
    @State private var isInitialHome = true
    @State private var visited: Set<Section> = [.home]
    @FocusState private var focusedTab: Section?
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    private enum Section: String, CaseIterable {
        case home = "Home"
        case series = "Series"
        case movies = "Movies"
        case search = "Search"
        case profiles = "Profiles"
    }

    var body: some View {
        VStack(spacing: 0) {
            ZStack {
                HStack {
                    Button("Profiles", systemImage: "person.crop.circle") { activate(.profiles) }
                        .labelStyle(.iconOnly)
                        .help("Profiles")
                        .buttonStyle(NavigationButtonStyle(isSelected: focusedTab == nil && section == .profiles))
                        .focusEffectDisabled()
                        .focused($focusedTab, equals: .profiles)
                        .onExitCommand { activate(.home) }
                    Spacer()
                    Image("SeplisLogo")
                        .resizable()
                        .frame(width: 40, height: 40)
                        .clipShape(Circle())
                        .accessibilityLabel("SEPLIS")
                }
                HStack(spacing: 16) {
                    ForEach([Section.search, .home, .series, .movies], id: \.self) { item in
                        Button {
                            activate(item)
                        } label: {
                            if item == .search { Image(systemName: "magnifyingglass") } else { Text(item.rawValue) }
                        }
                        .accessibilityLabel(item.rawValue)
                        .buttonStyle(NavigationButtonStyle(isSelected: focusedTab == nil && section == item))
                        .focusEffectDisabled()
                        .focused($focusedTab, equals: item)
                        .accessibilityAddTraits(section == item ? .isSelected : [])
                    }
                }
            }
            .font(.system(size: 26, weight: .semibold))
            .padding(.horizontal, LibraryStyle.horizontalInset)
            .frame(height: LibraryStyle.menuHeight)
            .focusSection()
            .defaultFocus($focusedTab, section, priority: .userInitiated)

            ZStack {
                ForEach(Section.allCases.filter { visited.contains($0) }, id: \.self) { tab in
                    page(tab)
                        .opacity(section == tab ? 1 : 0)
                        .transition(.opacity)
                        .disabled(section != tab)
                        .allowsHitTesting(section == tab)
                        .accessibilityHidden(section != tab)
                }
            }
            .animation(reduceMotion ? nil : .easeInOut(duration: 0.18), value: section)
        }
        .ignoresSafeArea(.container, edges: [.top, .horizontal])
        .task(id: focusedTab) {
            guard let tab = focusedTab, tab != .profiles, tab != section else { return }
            do { try await Task.sleep(for: .milliseconds(120)) } catch { return }
            guard focusedTab == tab else { return }
            activate(tab)
        }
    }

    @ViewBuilder
    private func page(_ tab: Section) -> some View {
        switch tab {
        case .home:
            HomeView(
                api: api, enteringFromMenu: focusedTab != nil, autoFocusOnLoad: isInitialHome,
                isActive: section == .home)
        case .series:
            CatalogView(
                api: api, kind: .series,
                enteringFromMenu: focusedTab != nil
            ).id(Section.series)
        case .movies:
            CatalogView(
                api: api, kind: .movie,
                enteringFromMenu: focusedTab != nil
            ).id(Section.movies)
        case .search: SearchView(api: api)
        case .profiles:
            ProfilesView(session: session).onExitCommand { activate(.home) }
        }
    }

    private func activate(_ tab: Section) {
        guard section != tab else { return }
        isInitialHome = false
        visited.insert(tab)
        section = tab
    }
}
