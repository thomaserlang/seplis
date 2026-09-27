import XCTest
@testable import seplis_apple_tv

nonisolated final class APIContractTests: XCTestCase {
    @MainActor func testEmptyEpisodeResponseIsNil() async throws {
        let client = APIClient(session: stubSession { _ in (204, Data()) })
        let episode: Episode? = try await client.getOptional("series/1/episode-to-watch")
        XCTAssertNil(episode)
    }

    @MainActor func testBearerTokenAndEncodedQuery() async throws {
        let session = stubSession { request in
            XCTAssertEqual(request.value(forHTTPHeaderField: "Authorization"), "Bearer account-one")
            XCTAssertEqual(request.url?.path, "/2/movies")
            let query = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)?.queryItems
            XCTAssertEqual(query?.first?.value, "a+b/= token")
            return (200, Data("{\"records\":[],\"cursor\":null}".utf8))
        }
        let _: Page<Media> = try await APIClient(token: "account-one", session: session)
            .get("movies", query: [.init(name: "cursor", value: "a+b/= token")])
    }

    @MainActor func testDeviceAuthorizationDatesAndSnakeCase() throws {
        for date in ["2026-09-26T20:00:00Z", "2026-09-26T20:00:00.123456Z"] {
            let data = Data("""
            {"device_code":"secret","user_code":"001234","verification_uri":"https://seplis.net/device",
             "verification_uri_complete":"https://seplis.net/device?code=001234","expires_at":"\(date)","poll_interval_seconds":3}
            """.utf8)
            let code = try APIClient.decoder().decode(DeviceAuthorization.self, from: data)
            XCTAssertEqual(code.userCode, "001234")
            XCTAssertEqual(code.pollIntervalSeconds, 3)
        }
    }

    @MainActor func testEpisodeUsesAbsoluteNumberForPlayback() throws {
        let episode = try APIClient.decoder().decode(Episode.self, from: Data("""
        {"number":25,"season":2,"episode":1,"title":"Return","user_watched":{"times":1,"position":0}}
        """.utf8))
        let target = PlaybackTarget(reference: .init(kind: .series, id: 42), title: "Series",
                                    episode: episode, fromBeginning: true)
        XCTAssertEqual(target.path, "series/42/episodes/25")
        XCTAssertEqual(episode.label, "S2 E1 - Return")
    }

    @MainActor func testPlayServerResolvesEachURLIndependently() throws {
        let response = PlayMediaResponse(hlsUrl: "https://cdn.example/hls.m3u8",
                                        keepAliveUrl: "/keep-alive?id=1", closeSessionUrl: "/close?id=1")
        let session = try response.session(relativeTo: URL(string: "https://play.example/mount")!)
        XCTAssertEqual(session.hlsURL.absoluteString, "https://cdn.example/hls.m3u8")
        XCTAssertEqual(session.keepAliveURL.absoluteString, "https://play.example/mount/keep-alive?id=1")
    }

    @MainActor func testCapabilitiesRequestNativeHLSAndSubtitles() {
        let capabilities = PlaybackCapabilities(videoCodecs: ["h264"], audioCodecs: ["aac"],
                                                hdrFormats: [], maxAudioChannels: 2, maxBitrate: 40_000_000)
        let query = Dictionary(uniqueKeysWithValues: capabilities.query(forceTranscode: false).map { ($0.name, $0.value) })
        XCTAssertEqual(query["format"], "hls")
        XCTAssertEqual(query["hls_include_all_subtitles"], "true")
        XCTAssertEqual(query["supported_video_codecs"], "h264")
        XCTAssertEqual(query["max_audio_channels"], "2")
    }

    @MainActor func testHomeFiltersMatchWeb() {
        XCTAssertEqual(HomeShelf.allCases.count, 13)
        for shelf in HomeShelf.allCases {
            XCTAssertTrue(shelf.query.contains(.init(name: "user_can_watch", value: "true")))
        }
        XCTAssertTrue(HomeShelf.movieWatchlist.query.contains(.init(name: "sort", value: "user_watchlist_added_at_desc")))
        XCTAssertEqual(HomeShelf.watched.path, "users/me/watched")
    }
}
