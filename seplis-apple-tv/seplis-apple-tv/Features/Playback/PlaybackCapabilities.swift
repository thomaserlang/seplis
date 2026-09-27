import AVFoundation
import VideoToolbox

struct PlaybackCapabilities {
    let videoCodecs: [String]
    let audioCodecs: [String]
    let hdrFormats: [String]
    let maxAudioChannels: Int
    let maxBitrate: Int

    static func current(maxBitrate: Int = PlaybackQuality.defaultBitrate, hdrEnabled: Bool = true) -> Self {
        var video = ["h264"]
        if VTIsHardwareDecodeSupported(kCMVideoCodecType_HEVC)
            || AVURLAsset.isPlayableExtendedMIMEType("video/mp4; codecs=\"hvc1.2.4.L153.B0\"") {
            video.insert("hevc", at: 0)
        }
        if VTIsHardwareDecodeSupported(kCMVideoCodecType_AV1) { video.append("av1") }
        let audioTypes = [("aac", "mp4a.40.2"), ("ac3", "ac-3"), ("eac3", "ec-3")]
        let audio = audioTypes.filter {
            AVURLAsset.isPlayableExtendedMIMEType("audio/mp4; codecs=\"\($0.1)\"")
        }.map(\.0)
        var hdr: [String] = []
        if hdrEnabled && AVPlayer.eligibleForHDRPlayback && video.contains("hevc") {
            hdr = ["hdr10", "hlg"]
            if AVURLAsset.isPlayableExtendedMIMEType("video/mp4; codecs=\"dvh1.05.06\"") {
                hdr.append("dovi")
            }
        }
        return Self(videoCodecs: video, audioCodecs: audio.isEmpty ? ["aac"] : audio,
                    hdrFormats: hdr,
                    // Content decoding limit; AVPlayer handles speaker routing/downmixing.
                    maxAudioChannels: 8,
                    maxBitrate: maxBitrate)
    }

    func query(forceTranscode: Bool, compatibilityFallback: Bool = false) -> [URLQueryItem] {
        var items: [URLQueryItem] = [
            .init(name: "supported_video_codecs", value: videoCodecs.joined(separator: ",")),
            .init(name: "supported_audio_codecs", value: audioCodecs.joined(separator: ",")),
            .init(name: "supported_video_containers", value: "mp4"),
            .init(name: "transcode_video_codec", value: !compatibilityFallback && videoCodecs.contains("hevc") ? "hevc" : "h264"),
            .init(name: "transcode_audio_codec", value: "aac"),
            .init(name: "max_audio_channels", value: String(maxAudioChannels)),
            .init(name: "max_video_bitrate", value: String(maxBitrate)),
            .init(name: "force_transcode", value: String(forceTranscode)),
            .init(name: "format", value: "hls"),
            .init(name: "start_time", value: "0"),
            .init(name: "hls_include_all_subtitles", value: "true"),
        ]
        if !compatibilityFallback, !hdrFormats.isEmpty {
            items.append(.init(name: "supported_hdr_formats", value: hdrFormats.joined(separator: ",")))
        }
        return items
    }
}
