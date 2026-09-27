import XCTest
@testable import seplis_apple_tv

nonisolated final class PlaybackQualityTests: XCTestCase {
    @MainActor func testMaxLabelIncludesCurrentSourceBitrate() {
        let rate = PlaybackQuality.label(5_200_000)
        XCTAssertEqual(PlaybackQuality.label(PlaybackQuality.maximum, sourceBitrate: 5_200_000), "Max (\(rate))")
        XCTAssertEqual(PlaybackQuality.label(3_000_000, sourceBitrate: 5_200_000), "3 Mbps")
        XCTAssertEqual(PlaybackQuality.label(PlaybackQuality.maximum), "Max")
        XCTAssertEqual(PlaybackQuality.label(PlaybackQuality.maximum, sourceBitrate: 0), "Max")
    }

    @MainActor func testBitratePersistsLocallyPerAccountAndReachesServerQuery() {
        let suite = "PlaybackQualityTests.\(UUID())"
        let defaults = UserDefaults(suiteName: suite)!
        defer { defaults.removePersistentDomain(forName: suite) }
        let api = APIClient()
        api.accountID = 1
        let preferences = PlaybackPreferences(api: api, seriesPath: nil, defaults: defaults)
        XCTAssertEqual(preferences.maxBitrate, PlaybackQuality.maximum)
        XCTAssertTrue(preferences.hdrEnabled)
        preferences.saveHDR(false)
        preferences.saveBitrate(3_000_000)
        let restored = PlaybackPreferences(api: api, seriesPath: nil, defaults: defaults)
        XCTAssertEqual(restored.maxBitrate, 3_000_000)
        XCTAssertFalse(restored.hdrEnabled)
        let caps = PlaybackCapabilities.current(maxBitrate: restored.maxBitrate)
        XCTAssertTrue(caps.query(forceTranscode: false).contains(.init(name: "max_video_bitrate", value: "3000000")))
        api.accountID = 2
        XCTAssertTrue(PlaybackPreferences(api: api, seriesPath: nil, defaults: defaults).hdrEnabled)
        XCTAssertEqual(PlaybackPreferences(api: api, seriesPath: nil, defaults: defaults).maxBitrate, PlaybackQuality.maximum)
        preferences.saveBitrate(-1)
        XCTAssertEqual(preferences.maxBitrate, 3_000_000)
    }
}
