import SwiftUI

struct AppTabsView: View {
    let session: AppSession
    let api: APIClient
    @State private var section: Section = .home
    @State private var isInitialHome = true
    @State private var visited: Set<Section> = [.home]
    @FocusState private var focusedTab: Section?
    @State private var isProfileFocused = false
    @State private var isProfileMenuPresented = false
    @State private var pendingTab: Section?
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    private enum Section: String, CaseIterable {
        case home = "Home"
        case series = "Series"
        case movies = "Movies"
        case search = "Search"
    }

    var body: some View {
        VStack(spacing: 0) {
            ZStack {
                HStack {
                    AccountMenuTrigger(accountName: session.user?.username ?? "Profiles", focusChanged: {
                        isProfileFocused = $0
                    }, open: openProfiles)
                    .frame(width: 260, height: 56)
                    .opacity(isProfileMenuPresented ? 0 : 1)
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
                            pendingTab = nil
                            activate(item)
                        } label: {
                            if item == .search { Image(systemName: "magnifyingglass") } else { Text(item.rawValue) }
                        }
                        .accessibilityLabel(item.rawValue)
                        .buttonStyle(NavigationButtonStyle(
                            isSelected: !isProfileFocused && !isProfileMenuPresented && focusedTab == nil && section == item))
                        .focusEffectDisabled()
                        .focused($focusedTab, equals: item)
                        .accessibilityAddTraits(!isProfileFocused && !isProfileMenuPresented && section == item ? .isSelected : [])
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
            .onExitCommand(perform: restoreTabFocus)
        }
        .disabled(isProfileMenuPresented)
        .overlay(alignment: .topLeading) {
            if isProfileMenuPresented {
                GeometryReader { geometry in
                    ProfilesPanel(session: session, maximumHeight: geometry.size.height - 48) {
                        isProfileMenuPresented = false
                        restoreTabFocus()
                    }
                    .padding(.leading, LibraryStyle.horizontalInset)
                    .padding(.top, 16)
                }
                .disabled(false)
                .transition(.asymmetric(insertion: .opacity, removal: .identity))
            }
        }
        .animation(reduceMotion || !isProfileMenuPresented ? nil : .easeOut(duration: 0.12), value: isProfileMenuPresented)
        .ignoresSafeArea(.container, edges: [.top, .horizontal])
        .onChange(of: focusedTab) {
            pendingTab = focusedTab == section ? nil : focusedTab
        }
        .task(id: pendingTab) {
            guard let tab = pendingTab else { return }
            do { try await Task.sleep(for: .milliseconds(300)) } catch { return }
            guard pendingTab == tab, focusedTab == tab else { return }
            activate(tab)
        }
    }

    @ViewBuilder
    private func page(_ tab: Section) -> some View {
        switch tab {
        case .home:
            HomeView(
                api: api, enteringFromMenu: isMenuFocused, autoFocusOnLoad: isInitialHome,
                isActive: section == .home)
        case .series:
            CatalogView(
                api: api, kind: .series,
                enteringFromMenu: isMenuFocused
            ).id(Section.series)
        case .movies:
            CatalogView(
                api: api, kind: .movie,
                enteringFromMenu: isMenuFocused
            ).id(Section.movies)
        case .search: SearchView(api: api)
        }
    }

    private var isMenuFocused: Bool { focusedTab != nil || isProfileFocused }

    private func restoreTabFocus() {
        pendingTab = nil
        focusedTab = section
    }

    private func openProfiles() {
        pendingTab = nil
        focusedTab = nil
        isProfileMenuPresented = true
    }

    private func activate(_ tab: Section) {
        guard section != tab else { return }
        isInitialHome = false
        visited.insert(tab)
        section = tab
    }
}
