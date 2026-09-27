import SwiftUI

struct PosterSkeletonRow: View {
    var body: some View {
        ScrollView(.horizontal) {
            HStack(spacing: 20) {
                ForEach(0..<10) { _ in
                    PosterSkeleton()
                }
            }
            .padding(.horizontal, LibraryStyle.horizontalInset)
            .padding(.top, 10)
            .padding(.bottom, 10)
        }
        .scrollIndicators(.hidden)
        .allowsHitTesting(false)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Loading titles")
    }
}
