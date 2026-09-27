import SwiftUI

struct PosterView: View {
    let poster: Poster?
    let title: String
    var width: CGFloat = 200
    var cornerRadius: CGFloat = 8

    var body: some View {
        AsyncImage(url: poster?.imageURL) { phase in
            switch phase {
            case .success(let image):
                image.resizable().scaledToFill()
            case .empty where poster?.imageURL != nil:
                PosterSkeleton(width: width, cornerRadius: cornerRadius)
            default:
                fallback
            }
        }
        .frame(width: width, height: width * 1.5)
        .clipShape(RoundedRectangle(cornerRadius: cornerRadius))
        .accessibilityLabel(title)
    }

    private var fallback: some View {
        ZStack {
            PosterSkeleton(width: width, cornerRadius: cornerRadius)
            VStack(spacing: 12) {
                Image(systemName: "film").font(.title2)
                Text(title).font(.caption).multilineTextAlignment(.center).lineLimit(3)
            }
            .foregroundStyle(.secondary)
            .padding(16)
        }
    }
}
