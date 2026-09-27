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
}
