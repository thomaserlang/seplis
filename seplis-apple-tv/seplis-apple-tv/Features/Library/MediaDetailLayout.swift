import SwiftUI

struct MediaDetailLayout<Content: View>: View {
    let poster: Poster?
    let content: Content

    init(poster: Poster?, @ViewBuilder content: () -> Content) {
        self.poster = poster
        self.content = content()
    }

    var body: some View {
        GeometryReader { geometry in
            let artworkWidth = geometry.size.height * 2 / 3
            HStack(spacing: 0) {
                ScrollView {
                    content
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.leading, max(64, geometry.size.width * 0.04))
                        .padding(.trailing, 48)
                        .padding(.vertical, 56)
                }
                .frame(maxWidth: .infinity)
                MediaDetailArtwork(poster: poster)
                    .frame(width: artworkWidth, height: geometry.size.height)
            }
            .frame(width: geometry.size.width, height: geometry.size.height)
        }
        .background(LibraryStyle.background)
        .ignoresSafeArea()
    }
}
