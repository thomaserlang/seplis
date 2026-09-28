import SwiftUI

struct ProfilesPanel: View {
    let session: AppSession
    let maximumHeight: CGFloat
    let close: () -> Void
    @State private var isAddingAccount = false
    @State private var isRemovingAccount = false
    @State private var profileToRemove: CurrentUser?
    @FocusState private var focusedItem: Item?

    private enum Item: Hashable {
        case profile(Int), add, finish, signOut, remove, back
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                if isRemovingAccount {
                    Text("Remove Account")
                        .font(.system(size: 26, weight: .semibold))
                        .padding(.bottom, 8)
                }
                if isRemovingAccount { removalRows } else { accountRows }
            }
            .padding(24)
        }
        .scrollBounceBehavior(.basedOnSize)
        .frame(width: 480, height: min(maximumHeight, panelHeight))
        .background(LibraryStyle.controlBackground, in: RoundedRectangle(cornerRadius: 8))
        .overlay { RoundedRectangle(cornerRadius: 8).strokeBorder(.white.opacity(0.15)) }
        .font(.system(size: 24))
        .buttonStyle(.bordered)
        .buttonBorderShape(.roundedRectangle(radius: 8))
        .controlSize(.small)
        .focusSection()
        .accessibilityIdentifier("profiles-panel")
        .task { focusedItem = session.user.map { .profile($0.id) } ?? .add }
        .onExitCommand {
            if isRemovingAccount {
                isRemovingAccount = false
                focusedItem = .remove
            } else { close() }
        }
        .onMoveCommand { direction in
            if direction == .right { close() }
        }
        .sheet(isPresented: $isAddingAccount) { DeviceLoginView(session: session) }
        .confirmationDialog("Remove \(profileToRemove?.username ?? "account") from this Apple TV?",
                            isPresented: Binding(get: { profileToRemove != nil }, set: { if !$0 { profileToRemove = nil } })) {
            Button("Remove Account", role: .destructive) {
                if let profileToRemove { session.removeProfile(profileToRemove) }
                profileToRemove = nil
                isRemovingAccount = false
                focusedItem = .add
            }
        }
    }

    private var accountRows: some View {
        Group {
            ForEach(session.profiles) { profile in
                Button {
                    if session.needsSignIn(profile) { isAddingAccount = true }
                    else if profile.id == session.user?.id { close() }
                    else { session.switchProfile(profile) }
                } label: {
                    HStack(spacing: 12) {
                        Image(systemName: "person.crop.circle")
                            .frame(width: 32)
                        Text(profile.username).lineLimit(1)
                        Spacer(minLength: 8)
                        if session.needsSignIn(profile) {
                            Text("Sign in again").font(.system(size: 18))
                        } else if profile.id == session.user?.id {
                            Image(systemName: "checkmark")
                        }
                    }
                    .frame(maxWidth: .infinity, minHeight: 32, alignment: .leading)
                }
                .focused($focusedItem, equals: .profile(profile.id))
                .accessibilityLabel(profile.username)
                .accessibilityValue(profile.id == session.user?.id ? "Active" : "")
                .accessibilityIdentifier("account-\(profile.id)")
            }
            Divider().padding(.vertical, 4)
            action("Add Account", icon: "person.badge.plus", item: .add) { isAddingAccount = true }
            if session.hasPendingSignIn {
                action("Finish Sign In", icon: "arrow.clockwise", item: .finish) {
                    Task { await session.retryPendingSignIn() }
                }
            }
            if let user = session.user {
                action("Sign Out of \(user.username)", icon: "rectangle.portrait.and.arrow.right", item: .signOut) {
                    profileToRemove = user
                }
            }
            if !otherProfiles.isEmpty {
                action("Remove Account", icon: "person.crop.circle.badge.minus", item: .remove) {
                    isRemovingAccount = true
                    focusedItem = .back
                }
            }
        }
    }

    private var removalRows: some View {
        Group {
            action("Back", icon: "chevron.left", item: .back) {
                isRemovingAccount = false
                focusedItem = .remove
            }
            ForEach(otherProfiles) { profile in
                action(profile.username, icon: "person.crop.circle.badge.minus", item: .profile(profile.id)) {
                    profileToRemove = profile
                }
            }
        }
    }

    private func action(_ title: String, icon: String, item: Item, perform: @escaping () -> Void) -> some View {
        Button(action: perform) {
            HStack(spacing: 12) {
                Image(systemName: icon).frame(width: 32)
                Text(title).lineLimit(1)
            }
            .frame(maxWidth: .infinity, minHeight: 32, alignment: .leading)
        }
        .focused($focusedItem, equals: item)
    }

    private var otherProfiles: [CurrentUser] { session.profiles.filter { $0.id != session.user?.id } }

    private var panelHeight: CGFloat {
        let rows = isRemovingAccount ? otherProfiles.count + 1 :
            session.profiles.count + 1 + (session.hasPendingSignIn ? 1 : 0) +
            (session.user != nil ? 1 : 0) + (otherProfiles.isEmpty ? 0 : 1)
        if isRemovingAccount { return 104 + CGFloat(rows) * 72 }
        if otherProfiles.isEmpty { return 52 + CGFloat(rows) * 72 }
        return 20 + CGFloat(rows) * 72
    }
}
