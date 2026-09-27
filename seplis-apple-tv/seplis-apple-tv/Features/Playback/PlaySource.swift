import Foundation

nonisolated struct PlayRequest: Decodable {
    let playId: String
    let playUrl: URL
}

nonisolated struct PlayStream: Decodable {
    let title: String?
    let language: String
    let groupIndex: Int?
    let forced: Bool
    var codec: String? = nil
    var channels: Int? = nil
    var key: String { "\(language):\(groupIndex.map(String.init) ?? "null")" }
    var displayTitle: String {
        guard let title, !title.isEmpty else { return language }
        return title
    }
}

nonisolated struct PlaySource: Decodable {
    let index: Int
    let duration: Double
    let bitrate: Double
    let codec: String
    let resolution: String
    let audio: [PlayStream]
    let subtitles: [PlayStream]
    var width: Int? = nil
    var height: Int? = nil
    var format: String? = nil
    var fps: Double? = nil
    var size: Int? = nil
    var videoColorRange: String? = nil
    var videoColorRangeType: String? = nil
    var mediaType: String? = nil
}

nonisolated struct PlayCandidate {
    let request: PlayRequest
    let source: PlaySource
    var label: String {
        var parts = [source.resolution, source.codec.uppercased()]
        if source.videoColorRange?.lowercased() == "hdr" {
            parts.append(source.videoColorRangeType?.lowercased() == "dovi" ? "Dolby Vision" : "HDR")
        }
        if source.bitrate > 0 {
            parts.append("\((source.bitrate / 1_000_000).formatted(.number.precision(.fractionLength(0...1)))) Mbps")
        }
        if let host = request.playUrl.host { parts.append(host) }
        return parts.joined(separator: " · ")
    }
}
