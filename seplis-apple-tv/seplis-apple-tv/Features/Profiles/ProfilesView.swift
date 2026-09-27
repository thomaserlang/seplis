import SwiftUI

struct ProfilesView: View {
    let session: AppSession
    @State private var isAddingAccount = false
    @State private var profileToRemove: CurrentUser?

    var body: some View {
        VStack(alignment: .leading, spacing: 28) {
            Text("Profiles").font(.system(size: 36, weight: .semibold))
            ScrollView {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 240, maximum: 280))], spacing: 28) {
                    ForEach(session.profiles) { profile in
                        Button {
                            if session.needsSignIn(profile) { isAddingAccount = true }
                            else { session.switchProfile(profile) }
                        } label: {
                            VStack(spacing: 20) {
                                Image(systemName: profile.id == session.user?.id ? "person.crop.circle.fill" : "person.crop.circle")
                                    .font(.system(size: 72))
                                Text(profile.username).lineLimit(1)
                                Text(session.needsSignIn(profile) ? "Sign in again" : profile.id == session.user?.id ? "Active" : " ")
                                    .font(.caption).foregroundStyle(.secondary)
                            }
                            .frame(width: 240, height: 210)
                        }
                        .buttonStyle(.card)
                        .accessibilityIdentifier("profile-\(profile.id)")
                        .contextMenu {
                            Button("Remove Account", systemImage: "person.crop.circle.badge.minus", role: .destructive) {
                                profileToRemove = profile
                            }
                        }
                    }
                }
                .padding(20)
            }
            .focusSection()
            HStack(spacing: 32) {
                Button("Add Account", systemImage: "person.badge.plus") { isAddingAccount = true }
                if let user = session.user {
                    Button("Sign Out of \(user.username)", systemImage: "rectangle.portrait.and.arrow.right") {
                        profileToRemove = user
                    }
                }
                if session.hasPendingSignIn {
                    Button("Finish Sign In", systemImage: "arrow.clockwise") {
                        Task { await session.retryPendingSignIn() }
                    }
                }
            }
            .frame(maxWidth: .infinity)
            .focusSection()
        }
        .padding(.horizontal, LibraryStyle.horizontalInset)
        .padding(.vertical, 32)
        .background(LibraryStyle.background.ignoresSafeArea())
        .sheet(isPresented: $isAddingAccount) { DeviceLoginView(session: session) }
        .onChange(of: session.sessionID) { _, _ in isAddingAccount = false }
        .confirmationDialog("Remove \(profileToRemove?.username ?? "account") from this Apple TV?",
                            isPresented: Binding(get: { profileToRemove != nil }, set: { if !$0 { profileToRemove = nil } })) {
            Button("Remove Account", role: .destructive) {
                if let profileToRemove { session.removeProfile(profileToRemove) }
                profileToRemove = nil
            }
        }
    }
}
