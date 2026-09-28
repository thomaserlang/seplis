import Foundation

extension Movie: MediaDetailInfo {
    var statusLabel: String? {
        guard let status else { return nil }
        let labels = ["Unknown", "Released", "In production", "Planned", "Cancelled", "Rumored"]
        return labels.indices.contains(status) && status != 0 ? labels[status] : nil
    }

    var detailFacts: [MediaDetailFact] {
        var facts: [MediaDetailFact] = []
        if let releaseDate { facts.append(.init(label: "Year", value: String(releaseDate.prefix(4)))) }
        if let runtime, runtime > 0 {
            let hours = runtime / 60
            let minutes = runtime % 60
            let value = hours == 0 ? "\(minutes)m" : minutes == 0 ? "\(hours)h" : "\(hours)h \(minutes)m"
            facts.append(.init(label: "Runtime", value: value))
        }
        if let language, !language.isEmpty {
            facts.append(.init(label: "Language", value: MediaFactFormat.language(language)))
        }
        if let rating { facts.append(.init(label: "IMDb", value: MediaFactFormat.rating(rating))) }
        if let budget, budget > 0 {
            facts.append(.init(label: "Budget", value: MediaFactFormat.money(budget)))
        }
        if let revenue, revenue > 0 {
            facts.append(.init(label: "Revenue", value: MediaFactFormat.money(revenue)))
        }
        return facts
    }
}
