import SwiftUI
import UIKit

struct ProfilesMenu: View {
    let session: AppSession
    let focusChanged: (Bool) -> Void
    let presentationChanged: (Bool) -> Void
    @State private var isAddingAccount = false
    @State private var profileToRemove: CurrentUser?

    var body: some View {
        ProfileMenuButton(accountName: session.user?.username ?? "Profiles", menu: menu,
                          focusChanged: focusChanged, presentationChanged: presentationChanged)
        .frame(width: 260, height: 56)
        .sheet(isPresented: $isAddingAccount) { DeviceLoginView(session: session) }
        .onChange(of: session.sessionID) { isAddingAccount = false }
        .confirmationDialog("Remove \(profileToRemove?.username ?? "account") from this Apple TV?",
                            isPresented: Binding(get: { profileToRemove != nil }, set: { if !$0 { profileToRemove = nil } })) {
            Button("Remove Account", role: .destructive) {
                if let profileToRemove { session.removeProfile(profileToRemove) }
                profileToRemove = nil
            }
        }
    }

    private var menu: UIMenu {
        let profiles = session.profiles.map { profile in
            UIAction(title: session.needsSignIn(profile) ? "\(profile.username) - Sign in again" : profile.username,
                     state: profile.id == session.user?.id ? .on : .off) { _ in selectProfile(profile.id) }
        }
        var accountActions = [UIAction(title: "Add Account", image: UIImage(systemName: "person.badge.plus")) { _ in
            isAddingAccount = true
        }]
        if session.hasPendingSignIn {
            accountActions.append(UIAction(title: "Finish Sign In", image: UIImage(systemName: "arrow.clockwise")) { _ in
                Task { await session.retryPendingSignIn() }
            })
        }
        var removalActions: [UIMenuElement] = []
        if let user = session.user {
            removalActions.append(UIAction(title: "Sign Out of \(user.username)",
                                           image: UIImage(systemName: "rectangle.portrait.and.arrow.right"),
                                           attributes: .destructive) { _ in profileToRemove = user })
        }
        let otherProfiles = session.profiles.filter { $0.id != session.user?.id }
        if !otherProfiles.isEmpty {
            removalActions.append(UIMenu(title: "Remove Account", image: UIImage(systemName: "person.crop.circle.badge.minus"),
                                         children: otherProfiles.map { profile in
                UIAction(title: profile.username, attributes: .destructive) { _ in profileToRemove = profile }
            }))
        }
        return UIMenu(children: [
            UIMenu(options: .displayInline, children: profiles),
            UIMenu(options: .displayInline, children: accountActions),
            UIMenu(options: .displayInline, children: removalActions),
        ])
    }

    private func selectProfile(_ id: Int) {
        guard let profile = session.profiles.first(where: { $0.id == id }), id != session.user?.id else { return }
        if session.needsSignIn(profile) { isAddingAccount = true }
        else { session.switchProfile(profile) }
    }
}
