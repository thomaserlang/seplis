import SwiftUI

struct MediaStateActions<MediaType: MediaDetailInfo>: View {
    let media: MediaType
    let isUpdating: Bool
    let onWatchlist: () -> Void
    let onFavorite: () -> Void

    var body: some View {
        HStack(spacing: 24) {
            MediaStateButton(title: "Watchlist", symbol: media.userWatchlist?.onWatchlist == true ? "bookmark.fill" : "bookmark",
                             isActive: media.userWatchlist?.onWatchlist == true,
                             color: .indigo, action: onWatchlist)
            MediaStateButton(title: "Favorite", symbol: media.userFavorite?.favorite == true ? "star.fill" : "star",
                             isActive: media.userFavorite?.favorite == true,
                             color: Color(red: 0.65, green: 0.29, blue: 0.02), action: onFavorite)
        }
        .disabled(isUpdating)
    }
}
