import SwiftUI

struct MediaDetailLayout<Header: View, Content: View>: View {
    let poster: Poster?
    let header: Header
    let content: Content

    init(poster: Poster?, @ViewBuilder header: () -> Header, @ViewBuilder content: () -> Content) {
        self.poster = poster
        self.header = header()
        self.content = content()
    }

    var body: some View {
        GeometryReader { geometry in
            let artworkWidth = geometry.size.height * 2 / 3
            HStack(spacing: 0) {
                VStack(alignment: .leading, spacing: 0) {
                    header
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.bottom, 24)
                    ScrollView {
                        content
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.bottom, 56)
                    }
                }
                .padding(.leading, max(64, geometry.size.width * 0.04))
                .padding(.trailing, 48)
                .padding(.top, 56)
                .frame(width: geometry.size.width - artworkWidth, height: geometry.size.height, alignment: .topLeading)
                MediaDetailArtwork(poster: poster)
                    .frame(width: artworkWidth, height: geometry.size.height)
            }
            .frame(width: geometry.size.width, height: geometry.size.height)
        }
        .background(LibraryStyle.background)
        .ignoresSafeArea()
    }
}
