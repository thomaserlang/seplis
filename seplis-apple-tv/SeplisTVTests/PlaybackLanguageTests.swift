import Synchronization
import XCTest

@testable import seplis_apple_tv

nonisolated final class PlaybackLanguageTests: XCTestCase {
    @MainActor func testAudioUsesSavedVariantThenWebLanguageOrder() {
        let media = source(audio: [stream("en", 0), stream("jpn", 1), stream("eng", 2)])
        XCTAssertEqual(PlaybackLanguages.audio(in: media, saved: "eng:2")?.key, "eng:2")
        XCTAssertEqual(PlaybackLanguages.audio(in: media, saved: nil)?.key, "jpn:1")
        XCTAssertEqual(
            PlaybackLanguages.audio(in: source(audio: [stream("deu", 0), stream("en", 1)]), saved: nil)?.key, "en:1")
    }

    @MainActor func testSubtitlesFollowWebDefaultsAndSavedPreference() {
        let source = source(subtitles: [stream("eng", 0), stream("dan", 1), stream("eng", 2)])
        let audio = stream("eng", 0)
        XCTAssertEqual(
            PlaybackLanguages.subtitle(in: source, saved: nil, audio: audio, preferredLanguages: ["da"])?.key, "dan:1")
        XCTAssertNil(PlaybackLanguages.subtitle(in: source, saved: nil, audio: audio, preferredLanguages: ["en"]))
        XCTAssertEqual(PlaybackLanguages.subtitle(in: source, saved: "eng:2", audio: audio)?.key, "eng:2")
        // A saved but unavailable language still requests subtitles, including when the fallback matches audio.
        XCTAssertEqual(
            PlaybackLanguages.subtitle(in: source, saved: "fra:0", audio: audio, preferredLanguages: ["eng"])?.key,
            "eng:0")
        XCTAssertEqual(
            PlaybackLanguages.subtitle(in: source, saved: nil, audio: stream("jpn", 0), preferredLanguages: [])?.key,
            "eng:0")
        XCTAssertTrue(PlaybackLanguages.matches("en-US", "eng"))
    }

    @MainActor func testPreferencesPersistPerAccountAndSyncPartialSeriesUpdates() async throws {
        let suite = "PlaybackLanguageTests.\(UUID())"
        let defaults = UserDefaults(suiteName: suite)!
        defer { defaults.removePersistentDomain(forName: suite) }
        let writes = Mutex<[Data]>([])
        let transport = stubSession { request in
            XCTAssertEqual(request.url?.path, "/2/series/7/user-settings")
            if request.httpMethod == "GET" {
                return (200, Data(#"{"audio_lang":"jpn:0","subtitle_lang":"eng:1"}"#.utf8))
            }
            XCTAssertEqual(request.httpMethod, "PUT")
            writes.withLock { $0.append(requestBody(request)) }
            return (204, Data())
        }
        let api = APIClient(session: transport)
        api.accountID = 1
        let preferences = PlaybackPreferences(api: api, seriesPath: "series/7", defaults: defaults)
        await preferences.load()
        XCTAssertEqual(preferences.audioKey, "jpn:0")
        XCTAssertEqual(preferences.subtitleKey, "eng:1")
        preferences.saveAudio("eng:0")
        preferences.saveSubtitle("dan:2")
        preferences.saveSubtitle(nil)
        await preferences.flush()
        XCTAssertNil(preferences.error)
        let savedBodies = writes.withLock { $0 }
        let bodies = try savedBodies.map { try JSONSerialization.jsonObject(with: $0) as! [String: Any] }
        XCTAssertEqual(bodies.count, 3)
        XCTAssertEqual(bodies[0]["audio_lang"] as? String, "eng:0")
        XCTAssertNil(bodies[0]["subtitle_lang"])
        XCTAssertEqual(bodies[1]["subtitle_lang"] as? String, "dan:2")
        XCTAssertTrue(bodies[2]["subtitle_lang"] is NSNull)
        let restored = PlaybackPreferences(api: api, seriesPath: nil, defaults: defaults)
        XCTAssertEqual(restored.audioKey, "eng:0")
        XCTAssertTrue(restored.subtitlesOff)
        api.accountID = 2
        let other = PlaybackPreferences(api: api, seriesPath: nil, defaults: defaults)
        XCTAssertNil(other.audioKey)
        XCTAssertFalse(other.subtitlesOff)
    }

    @MainActor private func stream(_ language: String, _ index: Int) -> PlayStream {
        PlayStream(title: nil, language: language, groupIndex: index, forced: false)
    }

    @MainActor private func source(audio: [PlayStream] = [], subtitles: [PlayStream] = []) -> PlaySource {
        PlaySource(
            index: 0, duration: 100, bitrate: 1000, codec: "h264", resolution: "1080p", audio: audio,
            subtitles: subtitles)
    }
}

private nonisolated func requestBody(_ request: URLRequest) -> Data {
    if let body = request.httpBody { return body }
    guard let stream = request.httpBodyStream else { return Data() }
    stream.open()
    defer { stream.close() }
    var result = Data()
    var buffer = [UInt8](repeating: 0, count: 1024)
    while stream.hasBytesAvailable {
        let count = stream.read(&buffer, maxLength: buffer.count)
        guard count > 0 else { break }
        result.append(contentsOf: buffer.prefix(count))
    }
    return result
}
