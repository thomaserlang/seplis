import Foundation

@MainActor
struct PlayServerClient {
    let session: URLSession
    init(session: URLSession = .shared) { self.session = session }

    func sources(for requests: [PlayRequest]) async throws -> [PlayCandidate] {
        guard !requests.isEmpty else {
            throw APIError.message("No play server has this title available for your account.")
        }
        var candidates: [PlayCandidate] = []
        var failures: [String] = []
        for request in requests.reversed() {
            try Task.checkCancellation()
            do {
                let data = try await fetch(request.playUrl.appending(path: "sources").addingQuery([
                    .init(name: "play_id", value: request.playId),
                ]), timeout: 3)
                let sources = try APIClient.decoder().decode([PlaySource].self, from: data)
                if sources.isEmpty {
                    failures.append("\(request.playUrl.host ?? "Play server"): no media files were returned.")
                }
                candidates += sources.map { PlayCandidate(request: request, source: $0) }
            } catch is CancellationError { throw CancellationError() }
            catch let error as URLError where error.code == .cancelled { throw CancellationError() }
            catch {
                failures.append("\(request.playUrl.host ?? "Play server"): \(PlayServerFailure.message(for: error))")
            }
        }
        guard !candidates.isEmpty else {
            throw APIError.message(failures.joined(separator: "\n"))
        }
        return candidates
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
