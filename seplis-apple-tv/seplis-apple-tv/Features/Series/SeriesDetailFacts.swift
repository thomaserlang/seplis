import Foundation

extension Series: MediaDetailInfo {
    var statusLabel: String? {
        guard let status else { return nil }
        let labels = ["Unknown", "Returning", "Ended", "Cancelled", "In production", "Planned"]
        return labels.indices.contains(status) && status != 0 ? labels[status] : nil
    }

    var detailFacts: [MediaDetailFact] {
        var facts: [MediaDetailFact] = []
        if let premiered {
            let start = String(premiered.prefix(4))
            var years = start
            if let ended {
                let end = String(ended.prefix(4))
                if end != start { years += "-\(end)" }
            }
            facts.append(.init(label: "Year", value: years))
        }
        if let statusLabel { facts.append(.init(label: "Status", value: statusLabel)) }
        if let runtime, runtime > 0 {
            facts.append(.init(label: "Runtime", value: "\(runtime) min"))
        }
        if let language, !language.isEmpty {
            facts.append(.init(label: "Language", value: MediaFactFormat.language(language)))
        }
        if let rating { facts.append(.init(label: "IMDb", value: MediaFactFormat.rating(rating))) }
        if let seasons, !seasons.isEmpty {
            facts.append(.init(label: seasons.count == 1 ? "Season" : "Seasons", value: String(seasons.count)))
        }
        if let totalEpisodes, totalEpisodes > 0 {
            facts.append(.init(label: "Episodes", value: String(totalEpisodes)))
        }
        return facts
    }
}
