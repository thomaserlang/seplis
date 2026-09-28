import SwiftUI

struct MediaDetailHeader<MediaType: MediaDetailInfo, Actions: View>: View {
    let media: MediaType
    let actions: Actions

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 6) {
                Text(media.displayTitle).font(.system(size: 42, weight: .semibold))
                if let originalTitle = media.originalTitle, originalTitle != media.displayTitle {
                    Text(originalTitle).font(.system(size: 21)).foregroundStyle(.secondary)
                }
                if let tagline = media.tagline, !tagline.isEmpty {
                    Text(tagline).font(.system(size: 21)).italic().foregroundStyle(.secondary)
                }
                if let status = media.statusLabel {
                    Text(status).font(.system(size: 19)).foregroundStyle(.secondary)
                }
            }
            let facts = media.detailFacts
            if !facts.isEmpty {
                HStack(alignment: .top, spacing: 30) {
                    ForEach(facts, id: \.label) { fact in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(fact.label.uppercased())
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundStyle(.secondary)
                            Text(fact.value)
                                .font(.system(size: 21, weight: .semibold))
                                .foregroundStyle(fact.label == "IMDb" ? .yellow : .primary)
                        }
                    }
                }
            }
            if let genres = media.genres, !genres.isEmpty {
                Text(genres.map(\.name).joined(separator: " · "))
                    .font(.system(size: 22)).foregroundStyle(.secondary)
            }
            if let plot = media.plot, !plot.isEmpty {
                Text(plot).font(.system(size: 24)).foregroundStyle(.secondary).lineLimit(5)
            }
            actions
        }
        .focusSection()
    }
}
