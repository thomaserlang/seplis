import SwiftUI

struct PosterSkeleton: View {
    var width: CGFloat = LibraryStyle.posterWidth
    var cornerRadius: CGFloat = 8

    var body: some View {
        RoundedRectangle(cornerRadius: cornerRadius)
            .fill(Color(white: 0.14))
            .frame(width: width, height: width * 1.5)
            .accessibilityHidden(true)
    }
}
