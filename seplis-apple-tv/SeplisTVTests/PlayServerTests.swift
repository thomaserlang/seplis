import XCTest
@testable import seplis_apple_tv

nonisolated final class PlayServerTests: XCTestCase {
    @MainActor private final class DiscoveryProbe {
        var started = Set<String>()
        var cancelled = Set<String>()
    }

    @MainActor private func discoveryRequests() -> [PlayRequest] {
        [PlayRequest(playId: "fast", playUrl: URL(string: "https://fast.example")!),
         PlayRequest(playId: "slow", playUrl: URL(string: "https://slow.example")!)]
    }

    @MainActor private func discoverySource() -> PlaySource {
        PlaySource(index: 0, duration: 120, bitrate: 2_000_000, codec: "h264",
                   resolution: "1080p", audio: [], subtitles: [])
    }

    @MainActor func testAvailableSourcesSkipSlowServerAfterGracePeriod() async throws {
        let probe = DiscoveryProbe()
        let source = discoverySource()
        let start = ContinuousClock.now
        let candidates = try await PlayServerClient.collectSources(for: discoveryRequests()) { request in
            probe.started.insert(request.playId)
            if request.playId == "slow" {
                do { try await Task.sleep(for: .seconds(30)) }
                catch { probe.cancelled.insert(request.playId); throw error }
            }
            return [source]
        }
        XCTAssertEqual(candidates.map { $0.request.playId }, ["fast"])
        XCTAssertEqual(probe.started, ["fast", "slow"])
        XCTAssertEqual(probe.cancelled, ["slow"])
        XCTAssertGreaterThanOrEqual(start.duration(to: .now), .milliseconds(1800))
        XCTAssertLessThan(start.duration(to: .now), .seconds(5))
    }

    @MainActor func testFirstUsableResponseAfterGracePeriodSkipsPendingServer() async throws {
        let source = discoverySource()
        let probe = DiscoveryProbe()
        let start = ContinuousClock.now
        let candidates = try await PlayServerClient.collectSources(for: discoveryRequests()) { request in
            do { try await Task.sleep(for: .milliseconds(request.playId == "fast" ? 2200 : 30_000)) }
            catch { probe.cancelled.insert(request.playId); throw error }
            return [source]
        }
        XCTAssertEqual(candidates.map { $0.request.playId }, ["fast"])
        XCTAssertEqual(probe.cancelled, ["slow"])
        XCTAssertLessThan(start.duration(to: .now), .seconds(5))
    }

    @MainActor func testEmptyResponseDoesNotEndDiscoveryAtGracePeriod() async throws {
        let source = discoverySource()
        let candidates = try await PlayServerClient.collectSources(for: discoveryRequests()) { request in
            if request.playId == "fast" { return [] }
            try await Task.sleep(for: .milliseconds(2200))
            return [source]
        }
        XCTAssertEqual(candidates.map { $0.request.playId }, ["slow"])
    }

    @MainActor func testCompletedDiscoveryPreservesServerOrderWithoutWaitingForGracePeriod() async throws {
        let source = discoverySource()
        let start = ContinuousClock.now
        let candidates = try await PlayServerClient.collectSources(for: discoveryRequests()) { request in
            if request.playId == "slow" { try await Task.sleep(for: .milliseconds(50)) }
            return [source]
        }
        XCTAssertEqual(candidates.map { $0.request.playId }, ["slow", "fast"])
        XCTAssertLessThan(start.duration(to: .now), .seconds(1))
    }

    @MainActor func testCancellingDiscoveryCancelsEveryPendingRequest() async {
        let probe = DiscoveryProbe()
        let requests = discoveryRequests()
        let task = Task {
            try await PlayServerClient.collectSources(for: requests) { request in
                probe.started.insert(request.playId)
                do { try await Task.sleep(for: .seconds(30)) }
                catch { probe.cancelled.insert(request.playId); throw error }
                return []
            }
        }
        while probe.started.count < requests.count { await Task.yield() }
        task.cancel()
        do {
            _ = try await task.value
            XCTFail("Expected cancellation")
        } catch { XCTAssertTrue(error is CancellationError) }
        XCTAssertEqual(probe.cancelled, ["fast", "slow"])
    }

    @MainActor func testServerDecimalDurationAndStreamDefaults() async throws {
        let transport = stubSession { _ in
            (200, Data("""
            [{"index":0,"duration":"7861.125","bitrate":8000000,"codec":"h264","resolution":"1080p",
              "audio":[{"title":"English","language":"eng","index":1,"codec":"aac","group_index":0}]}]
            """.utf8))
        }
        let candidates = try await PlayServerClient(session: transport).sources(for: [
            PlayRequest(playId: "token", playUrl: URL(string: "https://play.example")!)
        ])
        let source = try XCTUnwrap(candidates.first?.source)
        XCTAssertEqual(source.duration, 7861.125)
        XCTAssertEqual(source.audio.first?.key, "eng:0")
        XCTAssertEqual(source.audio.first?.forced, false)
        XCTAssertTrue(source.subtitles.isEmpty)
    }

    @MainActor func testSourceAllowsOmittedStreamLists() throws {
        let source = try APIClient.decoder().decode(PlaySource.self, from: Data("""
        {"index":0,"duration":"0","bitrate":0,"codec":"h264","resolution":"1080p"}
        """.utf8))
        XCTAssertEqual(source.duration, 0)
        XCTAssertTrue(source.audio.isEmpty)
        XCTAssertTrue(source.subtitles.isEmpty)
    }

    @MainActor func testInvalidDecimalDurationIsRejected() {
        for duration in ["not-a-number", "NaN", "Infinity", "-1"] {
            XCTAssertThrowsError(try APIClient.decoder().decode(PlaySource.self, from: Data("""
            {"index":0,"duration":"\(duration)","bitrate":0,"codec":"h264","resolution":"1080p"}
            """.utf8)))
        }
    }

    @MainActor func testEmptyServerListReportsAccountAvailability() async {
        do {
            _ = try await PlayServerClient().sources(for: [])
            XCTFail("Expected unavailable title")
        } catch {
            XCTAssertEqual(error.localizedDescription, "No play server has this title available for your account.")
        }
    }

    @MainActor func testMalformedSourcesIdentifyFieldWithoutExposingPlayToken() async {
        let transport = stubSession { _ in
            (200, Data("[{\"index\":0,\"duration\":null}]".utf8))
        }
        do {
            _ = try await PlayServerClient(session: transport).sources(for: [
                PlayRequest(playId: "secret-token", playUrl: URL(string: "https://play.example")!)
            ])
            XCTFail("Expected decoding error")
        } catch {
            XCTAssertTrue(error.localizedDescription.contains("duration"))
            XCTAssertTrue(error.localizedDescription.contains("play.example"))
            XCTAssertFalse(error.localizedDescription.contains("secret-token"))
        }
    }

    @MainActor func testTransportFailureIsNotReportedAsOfflineServer() async {
        let transport = stubSession { _ in throw URLError(.appTransportSecurityRequiresSecureConnection) }
        do {
            _ = try await PlayServerClient(session: transport).sources(for: [
                PlayRequest(playId: "secret-token", playUrl: URL(string: "http://play.example")!)
            ])
            XCTFail("Expected transport error")
        } catch {
            XCTAssertTrue(error.localizedDescription.contains("Apple blocked"))
            XCTAssertFalse(error.localizedDescription.contains("secret-token"))
        }
    }

    @MainActor func testCancelledDiscoveryDoesNotContinueToOtherServers() async {
        let transport = stubSession { _ in throw URLError(.cancelled) }
        do {
            _ = try await PlayServerClient(session: transport).sources(for: [
                PlayRequest(playId: "token", playUrl: URL(string: "https://play.example")!)
            ])
            XCTFail("Expected cancellation")
        } catch {
            XCTAssertTrue(error is CancellationError)
        }
    }

    @MainActor func testUnreachableServerFallsBackWithoutSendingAccountCredentials() async throws {
        let transport = stubSession { request in
            XCTAssertNil(request.value(forHTTPHeaderField: "Authorization"))
            if request.url?.host == "offline.example" { throw URLError(.cannotConnectToHost) }
            XCTAssertTrue(request.url!.absoluteString.contains("play_id=play-token"))
            return (200, Data("""
            [{"index":0,"duration":120,"bitrate":2000000,"codec":"h264","resolution":"1080p","audio":[],"subtitles":[]}]
            """.utf8))
        }
        let candidates = try await PlayServerClient(session: transport).sources(for: [
            PlayRequest(playId: "play-token", playUrl: URL(string: "https://online.example")!),
            PlayRequest(playId: "other", playUrl: URL(string: "https://offline.example")!),
        ])
        XCTAssertEqual(candidates.count, 1)
        XCTAssertEqual(candidates.first?.request.playUrl.host, "online.example")
    }

    @MainActor func testSwitchingAudioBackCreatesFreshUncachedSessions() async throws {
        let transport = stubSession { request in
            XCTAssertEqual(request.cachePolicy, .reloadIgnoringLocalCacheData)
            let query = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)!.queryItems!
            let session = try XCTUnwrap(query.first { $0.name == "session" }?.value)
            XCTAssertNotNil(UUID(uuidString: session))
            let audio = try XCTUnwrap(query.first { $0.name == "audio_lang" }?.value)
            return (200, Data("""
            {"hls_url":"/\(session)/\(audio).m3u8","keep_alive_url":"/keep/\(session)","close_session_url":"/close/\(session)"}
            """.utf8))
        }
        let client = PlayServerClient(session: transport)
        let candidate = PlayCandidate(request: PlayRequest(playId: "token", playUrl: URL(string: "https://play.example")!),
                                      source: PlaySource(index: 0, duration: 120, bitrate: 2_000_000, codec: "h264",
                                                         resolution: "1080p", audio: [], subtitles: []))
        var sessions = Set<URL>()
        for audio in ["eng:0", "jpn:0", "eng:0"] {
            let media = try await client.open(candidate, capabilities: .current(), audioKey: audio,
                                              subtitleKey: nil, forceTranscode: false)
            XCTAssertTrue(media.hlsURL.lastPathComponent.contains(audio))
            XCTAssertTrue(sessions.insert(media.keepAliveURL).inserted)
        }
    }

    @MainActor func testNativeRequestIncludesSelectedSourceAudioAndSubtitles() async throws {
        let transport = stubSession { request in
            XCTAssertNil(request.value(forHTTPHeaderField: "Authorization"))
            let query = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)!.queryItems!
            XCTAssertTrue(query.contains(.init(name: "source_index", value: "2")))
            XCTAssertTrue(query.contains(.init(name: "audio_lang", value: "jpn:0")))
            XCTAssertTrue(query.contains(.init(name: "hls_subtitle_lang", value: "eng:1")))
            XCTAssertTrue(query.contains(.init(name: "hls_include_all_subtitles", value: "true")))
            XCTAssertFalse(query.contains { $0.name == "supported_hdr_formats" })
            return (200, Data("""
            {"hls_url":"/stream.m3u8","keep_alive_url":"/keep","close_session_url":"/close"}
            """.utf8))
        }
        let source = PlaySource(index: 2, duration: 120, bitrate: 2_000_000, codec: "h264", resolution: "1080p", audio: [], subtitles: [])
        let candidate = PlayCandidate(request: PlayRequest(playId: "play-token", playUrl: URL(string: "https://play.example")!), source: source)
        let capabilities = PlaybackCapabilities(videoCodecs: ["h264"], audioCodecs: ["aac"], hdrFormats: [], maxAudioChannels: 2, maxBitrate: 40_000_000)
        let session = try await PlayServerClient(session: transport).open(candidate, capabilities: capabilities,
                                                                          audioKey: "jpn:0", subtitleKey: "eng:1", forceTranscode: false)
        XCTAssertEqual(session.hlsURL.absoluteString, "https://play.example/stream.m3u8")
    }
}
