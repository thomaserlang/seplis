import SwiftUI

struct MediaDetailView: View {
    let reference: MediaReference
    let api: APIClient
    var onClose: (() -> Void)?

    @ViewBuilder var body: some View {
        switch reference.kind {
        case .movie:
            MovieDetailView(reference: reference, api: api, onClose: onClose)
        case .series:
            SeriesDetailView(reference: reference, api: api, onClose: onClose)
        }
    }
}
