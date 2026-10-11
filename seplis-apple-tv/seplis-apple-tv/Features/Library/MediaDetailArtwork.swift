import SwiftUI

struct MediaDetailArtwork: View {
    let poster: Poster?

    var body: some View {
        GeometryReader { geometry in
            AsyncImage(url: poster?.originalURL) { phase in
                if case .success(let image) = phase {
                    image.resizable().scaledToFill()
                } else {
                    Color(white: 0.08)
                }
            }
            .frame(width: geometry.size.width, height: geometry.size.height)
            .clipped()
            .mask {
                LinearGradient(stops: [
                    .init(color: .clear, location: 0),
                    .init(color: .black, location: 0.14),
                    .init(color: .black, location: 1)
                ], startPoint: .leading, endPoint: .trailing)
            }
        }
        .accessibilityHidden(true)
    }
}
