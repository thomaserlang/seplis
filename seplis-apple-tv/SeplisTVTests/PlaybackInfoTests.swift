import XCTest
@testable import seplis_apple_tv

nonisolated final class PlaybackInfoTests: XCTestCase {
    @MainActor func testDecimalFrameRateEncodings() throws {
        for fps in [#""23.97602397602397602397602398""#, "23.976023976023976"] {
            let source = try APIClient.decoder().decode(PlaySource.self, from: Data("""
            {"index":0,"duration":"120","bitrate":1000000,"codec":"hevc","resolution":"2160p",
             "width":3840,"height":2160,"fps":\(fps),"size":270000000,
             "audio":[{"language":"eng","codec":"eac3","channels":6}]}
            """.utf8))
            XCTAssertEqual(try XCTUnwrap(source.fps), 24000.0 / 1001.0, accuracy: 0.00001)
            XCTAssertEqual(source.width, 3840)
            XCTAssertEqual(source.height, 2160)
            XCTAssertEqual(source.size, 270000000)
            XCTAssertEqual(source.audio.first?.channels, 6)
        }
    }

    @MainActor func testInvalidFrameRateIsNotSilentlyDiscarded() {
        for value in ["null", "{}", "true", #""N/A""#, #""NaN""#, #""Infinity""#, #""24000/1001""#, "-1"] {
            XCTAssertThrowsError(try APIClient.decoder().decode(PlaySource.self, from: Data("""
            {"index":0,"duration":120,"bitrate":1000000,"codec":"h264","resolution":"720p",
             "fps":\(value)}
            """.utf8)))
        }
        XCTAssertThrowsError(try APIClient.decoder().decode(PlayMediaResponse.self, from: Data(#"""
        {"hls_url":"/hls.m3u8","keep_alive_url":"/keep","close_session_url":"/close",
         "transcode_decision":{"video":null}}
        """#.utf8)))
    }

    @MainActor func testOriginalMetadataDecodesServerFields() throws {
        let source = try APIClient.decoder().decode(PlaySource.self, from: Data(#"""
        {"index":0,"duration":"120.5","bitrate":18000000,"codec":"hevc","resolution":"2160p",
         "width":3840,"height":2160,"format":"matroska","fps":"23.976","size":270000000,
         "video_color_range":"HDR","video_color_range_type":"HDR10",
         "audio":[{"language":"eng","group_index":0,"codec":"eac3","channels":6}]}
        """#.utf8))
        XCTAssertEqual(source.width, 3840)
        XCTAssertEqual(source.height, 2160)
        XCTAssertEqual(source.format, "matroska")
        XCTAssertEqual(source.fps, 23.976)
        XCTAssertEqual(source.videoColorRangeType, "HDR10")
        XCTAssertEqual(source.audio.first?.codec, "eac3")
        XCTAssertEqual(source.audio.first?.channels, 6)
    }

    @MainActor func testPlaybackDecisionSurvivesSessionCreation() throws {
        for method in ["direct_play", "remux", "transcode"] {
            let action = method == "transcode" ? "transcode" : "copy"
            let response = try APIClient.decoder().decode(PlayMediaResponse.self, from: Data("""
            {"hls_url":"/hls.m3u8","keep_alive_url":"/keep","close_session_url":"/close",
             "transcode_decision":{"method":"\(method)",
              "direct_play":{"supported":false,"blockers":[]},
              "video":{"action":"copy","source_codec":"hevc","target_codec":"hevc","blockers":[]},
              "audio":{"action":"\(action)","source_codec":"eac3","target_codec":"aac",
               "blockers":[{"code":"unsupported_codec","scope":"audio"}]}}}
            """.utf8))
            let session = try response.session(relativeTo: URL(string: "https://play.example.test")!)
            let decision = try XCTUnwrap(session.decision)
            XCTAssertEqual(decision.playbackMethod, method == "transcode" ? "Transcoding" : "Direct Stream")
            XCTAssertEqual(decision.video.label, "HEVC (copy)")
            if method == "transcode" {
                XCTAssertEqual(decision.audio.label, "EAC3 -> AAC (transcode)")
                XCTAssertEqual(decision.reasons, ["Audio: Unsupported codec"])
            } else if method == "direct_play" {
                XCTAssertEqual(decision.reasons, ["Player selected HLS delivery."])
            }
        }
    }

    @MainActor func testMissingOptionalInfoDoesNotPreventPlayback() throws {
        let response = try APIClient.decoder().decode(PlayMediaResponse.self, from: Data(#"""
        {"hls_url":"/hls.m3u8","keep_alive_url":"/keep","close_session_url":"/close"}
        """#.utf8))
        XCTAssertNil(response.transcodeDecision)
        let source = try APIClient.decoder().decode(PlaySource.self, from: Data(#"""
        {"index":0,"duration":120,"bitrate":1000000,"codec":"h264","resolution":"720p"}
        """#.utf8))
        XCTAssertNil(source.format)
        XCTAssertEqual(source.fps, 0)
    }
}
