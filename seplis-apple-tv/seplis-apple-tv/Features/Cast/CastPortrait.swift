import SwiftUI

struct CastPortrait: View {
    let person: CastPerson
    let isFocused: Bool
    static let width: CGFloat = 140

    var body: some View {
        AsyncImage(url: person.profileImage?.imageURL) { phase in
            if case .success(let image) = phase {
                image.resizable().scaledToFill()
            } else {
                ZStack {
                    Color(white: 0.12)
                    Image(systemName: "person.crop.square")
                        .font(.system(size: 48))
                        .foregroundStyle(.secondary)
                }
            }
        }
        .frame(width: Self.width, height: Self.width * 1.5)
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .overlay {
            RoundedRectangle(cornerRadius: 8)
                .strokeBorder(isFocused ? .white : .clear, lineWidth: 3)
        }
        .scaleEffect(isFocused ? 1.05 : 1)
        .animation(.easeOut(duration: 0.15), value: isFocused)
    }
}
