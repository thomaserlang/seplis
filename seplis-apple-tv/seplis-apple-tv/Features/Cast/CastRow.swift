import SwiftUI

struct CastRow: View {
    let reference: MediaReference
    let api: APIClient
    @State private var model = CastRowModel()
    @FocusState private var focusedPerson: Int?
    @Namespace private var focusNamespace

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            if !model.members.isEmpty || model.isLoading || !model.hasLoaded || model.error != nil {
                HStack(alignment: .firstTextBaseline, spacing: 18) {
                    Text("Top Cast").font(.system(size: 28, weight: .medium)).foregroundStyle(.secondary)
                    if let member = model.members.first(where: { $0.id == focusedPerson }) {
                        Text(member.person.name)
                            .font(.system(size: 22, weight: .medium))
                            .foregroundStyle(member.roles.isEmpty ? .primary : .secondary)
                            .lineLimit(1)
                        if !member.roles.isEmpty {
                            Text("·").foregroundStyle(.secondary)
                            Text(member.roles.joined(separator: " / "))
                                .font(.system(size: 21))
                                .lineLimit(1)
                        }
                    }
                }
                .frame(height: 42)
                ScrollView(.horizontal) {
                    LazyHStack(alignment: .top, spacing: 20) {
                        ForEach(model.members) { member in
                            CastPortrait(person: member.person, isFocused: focusedPerson == member.id)
                                .focusable()
                                .focusEffectDisabled()
                                .focused($focusedPerson, equals: member.id)
                                .prefersDefaultFocus(member.id == model.members.first?.id, in: focusNamespace)
                                .accessibilityElement(children: .ignore)
                                .accessibilityLabel(([member.person.name] + member.roles).joined(separator: ", "))
                                .accessibilityIdentifier("cast-person-\(member.id)")
                                .onAppear {
                                    guard model.error == nil,
                                          model.members.suffix(5).contains(where: { $0.id == member.id }) else { return }
                                    Task { await model.load(reference: reference, api: api, more: true) }
                                }
                        }
                        if model.isLoading || !model.hasLoaded && model.error == nil {
                            ForEach(0..<8, id: \.self) { _ in
                                PosterSkeleton(width: CastPortrait.width)
                            }
                        }
                        if let error = model.error {
                            FailureView(message: error) {
                                Task { await model.load(reference: reference, api: api, more: model.hasLoaded) }
                            }
                        }
                    }
                    .padding(8)
                }
                .scrollClipDisabled()
            }
        }
        .focusSection()
        .focusScope(focusNamespace)
        .defaultFocus($focusedPerson, model.members.first?.id, priority: .userInitiated)
        .task(id: reference) { if !model.hasLoaded { await model.load(reference: reference, api: api) } }
    }
}
