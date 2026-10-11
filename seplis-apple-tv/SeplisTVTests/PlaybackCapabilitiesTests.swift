import XCTest
@testable import seplis_apple_tv

nonisolated final class PlaybackCapabilitiesTests: XCTestCase {
    @MainActor func testHEVCIsAdvertisedAndPreferredWithoutForcingTranscoding() {
        let capabilities = PlaybackCapabilities(videoCodecs: ["hevc", "h264"], audioCodecs: ["aac", "eac3"],
                                                hdrFormats: ["hdr10"], maxAudioChannels: 8, maxBitrate: PlaybackQuality.maximum)
        let query = capabilities.query(forceTranscode: false)
        XCTAssertTrue(query.contains(.init(name: "supported_video_codecs", value: "hevc,h264")))
        XCTAssertTrue(query.contains(.init(name: "transcode_video_codec", value: "hevc")))
        XCTAssertTrue(query.contains(.init(name: "force_transcode", value: "false")))
        XCTAssertTrue(query.contains(.init(name: "max_audio_channels", value: "8")))
        XCTAssertTrue(query.contains(.init(name: "max_width", value: "3840")))
        XCTAssertTrue(query.contains(.init(name: "supported_hdr_formats", value: "hdr10")))
        XCTAssertTrue(capabilities.query(forceTranscode: true).contains(.init(name: "transcode_video_codec", value: "hevc")))
        XCTAssertTrue(capabilities.query(forceTranscode: true, compatibilityFallback: true).contains(.init(name: "transcode_video_codec", value: "h264")))
    }

    @MainActor func testHDROffDoesNotAdvertiseHDRFormats() {
        let capabilities = PlaybackCapabilities.current(hdrEnabled: false)
        XCTAssertTrue(capabilities.hdrFormats.isEmpty)
        XCTAssertFalse(capabilities.query(forceTranscode: false).contains { $0.name == "supported_hdr_formats" })
    }

    @MainActor func testContentChannelsAreNotLimitedToSpeakerRoute() {
        XCTAssertEqual(PlaybackCapabilities.current().maxAudioChannels, 8)
    }

    @MainActor func testWidthUsesBitrateAndRequestedTranscodeCodec() {
        let capabilities = PlaybackCapabilities(videoCodecs: ["hevc", "h264"], audioCodecs: ["aac"],
                                                hdrFormats: [], maxAudioChannels: 8, maxBitrate: 1_500_000)
        XCTAssertTrue(capabilities.query(forceTranscode: false).contains(.init(name: "max_width", value: "1920")))
        XCTAssertTrue(capabilities.query(forceTranscode: true, compatibilityFallback: true)
            .contains(.init(name: "max_width", value: "1280")))
        let unlimited = PlaybackCapabilities(videoCodecs: ["h264"], audioCodecs: ["aac"],
                                             hdrFormats: [], maxAudioChannels: 8, maxBitrate: 0)
        XCTAssertFalse(unlimited.query(forceTranscode: false).contains { $0.name == "max_width" })
    }

    @MainActor func testWidthThresholdBoundaries() {
        let limits = [
            "h264": [1_000_000, 2_000_000, 5_000_000, 12_000_000],
            "hevc": [500_000, 1_000_000, 3_000_000, 8_000_000],
            "av1": [300_000, 800_000, 2_000_000, 6_000_000],
        ]
        let widths = [854, 1280, 1920, 2560, 3840]
        for (codec, thresholds) in limits {
            for (index, bitrate) in thresholds.enumerated() {
                XCTAssertEqual(PlaybackResolution.recommendWidth(bitrate: bitrate - 1, codec: codec), widths[index])
                XCTAssertEqual(PlaybackResolution.recommendWidth(bitrate: bitrate, codec: codec), widths[index + 1])
            }
        }
        XCTAssertEqual(PlaybackResolution.recommendWidth(bitrate: 1_500_000, codec: "h265"), 1920)
        XCTAssertEqual(PlaybackResolution.recommendWidth(bitrate: 1_500_000, codec: "unknown"), 3840)
    }
}
