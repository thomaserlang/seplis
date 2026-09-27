import AVFoundation

enum PlaybackSourceSelection {
    static func preferredIndex(
        in candidates: [PlayCandidate], capabilities: PlaybackCapabilities,
        canPlayMediaType: (String) -> Bool = { AVURLAsset.isPlayableExtendedMIMEType($0) }
    ) -> Int? {
        let withinLimit = candidates.indices.filter { candidates[$0].source.bitrate <= Double(capabilities.maxBitrate) }
        let compatible = withinLimit.filter {
            let source = candidates[$0].source
            guard capabilities.videoCodecs.contains(source.codec) else { return false }
            return source.videoColorRange?.lowercased() != "hdr"
                || capabilities.hdrFormats.contains(source.videoColorRangeType?.lowercased() ?? "")
        }
        // Like the web player, prefer playable files within the bitrate limit.
        // Native HLS can remux supported video, so container alone need not cost us 4K.
        let pool = compatible.isEmpty ? withinLimit : compatible
        guard !pool.isEmpty else { return candidates.indices.first }
        return pool.sorted { left, right in
            let lhs = candidates[left].source
            let rhs = candidates[right].source
            let leftWidth = lhs.width ?? resolutionWidth(lhs.resolution)
            let rightWidth = rhs.width ?? resolutionWidth(rhs.resolution)
            if leftWidth != rightWidth { return leftWidth > rightWidth }
            let leftDirect = lhs.mediaType.map(canPlayMediaType) ?? false
            let rightDirect = rhs.mediaType.map(canPlayMediaType) ?? false
            if leftDirect != rightDirect { return leftDirect }
            return left < right
        }.first
    }

    private static func resolutionWidth(_ resolution: String) -> Int {
        switch resolution.lowercased() {
        case "8k", "4320p": 7680
        case "4k", "2160p": 3840
        case "1440p": 2560
        case "1080p": 1920
        case "720p": 1280
        case "480p": 854
        default: 0
        }
    }
}
