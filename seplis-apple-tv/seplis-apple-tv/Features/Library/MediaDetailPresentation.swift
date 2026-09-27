import SwiftUI

struct MediaDetailPresentation: ViewModifier {
    @Binding var reference: MediaReference?
    let api: APIClient

    func body(content: Content) -> some View {
        content.disabled(reference != nil).fullScreenCover(isPresented: Binding(
            get: { reference != nil },
            set: { if !$0 { reference = nil } }
        )) {
            if let reference {
                NavigationStack {
                    MediaDetailView(reference: reference, api: api)
                        .navigationDestination(for: MediaReference.self) { destination in
                            MediaDetailView(reference: destination, api: api)
                        }
                }
                .background(LibraryStyle.background.ignoresSafeArea())
                .buttonBorderShape(.roundedRectangle(radius: 8))
                .buttonStyle(LibraryButtonStyle())
                .focusEffectDisabled()
                .disabled(false)
            }
        }
    }
}
