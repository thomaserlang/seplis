import Foundation

@MainActor
struct PlayServerClient {
    let session: URLSession
    init(session: URLSession = .shared) { self.session = session }

    func sources(for requests: [PlayRequest]) async throws -> [PlayCandidate] {
        try await Self.collectSources(for: requests) { request in
            let data = try await fetch(request.playUrl.appending(path: "sources").addingQuery([
                .init(name: "play_id", value: request.playId),
            ]), timeout: 20)
            return try APIClient.decoder().decode([PlaySource].self, from: data)
        }
    }

    private struct SourceResponse: Sendable {
        let index: Int
        let candidates: [PlayCandidate]
        let failure: String?
    }

    static func collectSources(
        for requests: [PlayRequest],
        loadSources: @escaping @MainActor @Sendable (PlayRequest) async throws -> [PlaySource]
    ) async throws -> [PlayCandidate] {
        try Task.checkCancellation()
        guard !requests.isEmpty else {
            throw APIError.message("No play server has this title available for your account.")
        }
        return try await withThrowingTaskGroup(of: SourceResponse?.self) { group in
            defer { group.cancelAll() }
            group.addTask {
                try await Task.sleep(for: .seconds(2))
                return nil
            }
            for (index, request) in requests.reversed().enumerated() {
                group.addTask { @MainActor in
                    do {
                        let sources = try await loadSources(request)
                        let failure = sources.isEmpty
                            ? "\(request.playUrl.host ?? "Play server"): no media files were returned." : nil
                        return SourceResponse(index: index,
                            candidates: sources.map { PlayCandidate(request: request, source: $0) }, failure: failure)
                    } catch is CancellationError { throw CancellationError() }
                    catch let error as URLError where error.code == .cancelled { throw CancellationError() }
                    catch {
                        return SourceResponse(index: index, candidates: [],
                            failure: "\(request.playUrl.host ?? "Play server"): \(PlayServerFailure.message(for: error))")
                    }
                }
            }
            var responses: [SourceResponse] = []
            var gracePeriodElapsed = false
            for try await response in group {
                try Task.checkCancellation()
                if let response {
                    responses.append(response)
                } else {
                    gracePeriodElapsed = true
                }
                if responses.count == requests.count ||
                    (gracePeriodElapsed && responses.contains { !$0.candidates.isEmpty }) {
                    break
                }
            }
            responses.sort { $0.index < $1.index }
            let candidates = responses.flatMap(\.candidates)
            guard !candidates.isEmpty else {
                throw APIError.message(responses.compactMap(\.failure).joined(separator: "\n"))
            }
            return candidates
        }
    }

    func open(
        _ candidate: PlayCandidate, capabilities: PlaybackCapabilities,
        audioKey: String?, subtitleKey: String?, forceTranscode: Bool, compatibilityFallback: Bool = false
    ) async throws -> PlaySession {
        var query = capabilities.query(forceTranscode: forceTranscode, compatibilityFallback: compatibilityFallback) + [
            URLQueryItem(name: "play_id", value: candidate.request.playId),
            URLQueryItem(name: "source_index", value: String(candidate.source.index)),
            URLQueryItem(name: "session", value: UUID().uuidString),
        ]
        if let audioKey { query.append(.init(name: "audio_lang", value: audioKey)) }
        if let subtitleKey { query.append(.init(name: "hls_subtitle_lang", value: subtitleKey)) }
        let data = try await fetch(candidate.request.playUrl.appending(path: "request-media").addingQuery(query))
        return try APIClient.decoder().decode(PlayMediaResponse.self, from: data)
            .session(relativeTo: candidate.request.playUrl)
    }

    func keepAlive(_ playback: PlaySession) async throws { _ = try await fetch(playback.keepAliveURL) }
    func close(_ playback: PlaySession) async {
        // Cleanup must still reach the server when the playback task has been cancelled.
        await Task { _ = try? await fetch(playback.closeURL, timeout: 5) }.value
    }

    private func fetch(_ url: URL, timeout: TimeInterval = 30) async throws -> Data {
        guard ["https", "http"].contains(url.scheme), url.host != nil else { throw APIError.invalidResponse }
        // Never attach the Seplis bearer token to play-server or media URLs.
        let (data, response) = try await session.data(for: URLRequest(
            url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: timeout))
        guard let response = response as? HTTPURLResponse else { throw APIError.invalidResponse }
        guard (200..<300).contains(response.statusCode) else { throw APIError.http(response.statusCode, data) }
        return data
    }
}
