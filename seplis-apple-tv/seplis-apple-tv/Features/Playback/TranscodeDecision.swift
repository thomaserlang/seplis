import Foundation

nonisolated struct TranscodeDecision: Decodable {
    let method: String
    let directPlay: DirectPlayDecision
    let video: StreamDecision
    let audio: StreamDecision

    // The native player always uses the HLS URL, even when direct play is supported.
    var playbackMethod: String { method == "transcode" ? "Transcoding" : "Direct Stream" }

    var reasons: [String] {
        let blockers = directPlay.blockers
            + (video.action == "transcode" ? video.blockers : [])
            + (audio.action == "transcode" ? audio.blockers : [])
        var result = method == "direct_play" ? ["Player selected HLS delivery."] : []
        for blocker in blockers where !result.contains(blocker.label) { result.append(blocker.label) }
        return result
    }
}

nonisolated struct DirectPlayDecision: Decodable {
    let blockers: [PlaybackBlocker]
}

nonisolated struct StreamDecision: Decodable {
    let action: String
    let sourceCodec: String
    let targetCodec: String
    let blockers: [PlaybackBlocker]

    var label: String {
        action == "copy" ? "\(sourceCodec.uppercased()) (copy)"
            : "\(sourceCodec.uppercased()) -> \(targetCodec.uppercased()) (transcode)"
    }
}

nonisolated struct PlaybackBlocker: Decodable {
    let code: String
    let scope: String
    let limitKind: String?

    var label: String {
        let reason: String
        switch code {
        case "forced": reason = "Transcoding requested"
        case "unsupported_codec": reason = "Unsupported codec"
        case "unsupported_hdr": reason = "Unsupported HDR format"
        case "limit_exceeded": reason = "\((limitKind ?? "playback").replacingOccurrences(of: "_", with: " ")) limit exceeded"
        case "missing_keyframes": reason = "Missing keyframes"
        case "video_transcode_requires_audio_transcode": reason = "Video transcoding requires audio transcoding"
        case "unsupported_container": reason = "Unsupported container"
        case "client_audio_track_switch_unsupported": reason = "Selected audio track requires transcoding"
        default: reason = code.replacingOccurrences(of: "_", with: " ")
        }
        return "\(scope.capitalized): \(reason)"
    }
}
