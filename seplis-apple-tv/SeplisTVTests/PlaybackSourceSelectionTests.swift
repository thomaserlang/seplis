import XCTest
@testable import seplis_apple_tv

nonisolated final class PlaybackSourceSelectionTests: XCTestCase {
    @MainActor private var capabilities: PlaybackCapabilities {
        PlaybackCapabilities(videoCodecs: ["h264", "hevc"], audioCodecs: ["aac"], hdrFormats: ["hdr10"],
                             maxAudioChannels: 6, maxBitrate: 40_000_000)
    }

    @MainActor func testPrefersSupported4KOverFirst1080pSource() {
        let sources = [candidate("1080p", codec: "h264"), candidate("4K", codec: "hevc")]
        XCTAssertEqual(PlaybackSourceSelection.preferredIndex(in: sources, capabilities: capabilities), 1)
    }

    @MainActor func testDefaultQualityAllowsHighBitrate4KButRespectsExplicitLimit() {
        let sources = [candidate("1080p", codec: "h264"), candidate("4K", codec: "hevc", bitrate: 80_000_000)]
        let defaults = PlaybackCapabilities(videoCodecs: ["h264", "hevc"], audioCodecs: ["aac"], hdrFormats: ["hdr10"],
                                            maxAudioChannels: 6, maxBitrate: PlaybackQuality.defaultBitrate)
        XCTAssertEqual(PlaybackSourceSelection.preferredIndex(in: sources, capabilities: defaults), 1)
        XCTAssertEqual(PlaybackSourceSelection.preferredIndex(in: sources, capabilities: capabilities), 0)
    }

    @MainActor func testAvoidsUnsupportedCodecHDROrExcessiveBitrate() {
        let baseline = candidate("1080p", codec: "h264")
        for source in [candidate("4K", codec: "vp9"), candidate("4K", codec: "hevc", bitrate: 80_000_000),
                       candidate("4K", codec: "hevc", hdr: "dovi")] {
            XCTAssertEqual(PlaybackSourceSelection.preferredIndex(in: [source, baseline], capabilities: capabilities), 1)
        }
        XCTAssertEqual(PlaybackSourceSelection.preferredIndex(
            in: [baseline, candidate("4K", codec: "hevc", hdr: "hdr10")], capabilities: capabilities), 1)
    }

    @MainActor func testNativeMediaTypeBreaksQualityTieAndFallbacksAreStable() {
        var native = candidate("1080p", codec: "h264")
        var source = native.source
        source.mediaType = "video/mp4"
        native = PlayCandidate(request: native.request, source: source)
        XCTAssertEqual(PlaybackSourceSelection.preferredIndex(
            in: [candidate("1080p", codec: "h264"), native], capabilities: capabilities,
            canPlayMediaType: { $0 == "video/mp4" }), 1)
        XCTAssertNil(PlaybackSourceSelection.preferredIndex(in: [], capabilities: capabilities))
        XCTAssertEqual(PlaybackSourceSelection.preferredIndex(
            in: [candidate("4K", codec: "vp9", bitrate: 80_000_000)], capabilities: capabilities), 0)
    }

    @MainActor private func candidate(_ resolution: String, codec: String, bitrate: Double = 20_000_000,
                                     hdr: String? = nil) -> PlayCandidate {
        var source = PlaySource(index: 0, duration: 120, bitrate: bitrate, codec: codec,
                                resolution: resolution, audio: [], subtitles: [])
        source.videoColorRange = hdr == nil ? "sdr" : "hdr"
        source.videoColorRangeType = hdr
        return PlayCandidate(request: PlayRequest(playId: "test", playUrl: URL(string: "https://play.example.test")!),
                             source: source)
    }
}
