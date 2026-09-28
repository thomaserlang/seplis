import AVFoundation
import AVKit
import Foundation
import Observation

@MainActor @Observable
final class PlaybackModel {
    let target: PlaybackTarget
    private(set) var player = AVPlayer()
    private(set) var candidates: [PlayCandidate] = []
    private(set) var selectedSource = 0
    private(set) var audioKey: String?
    private(set) var nextEpisode: Episode?
    private(set) var progress: PlaybackProgress?
    private(set) var isLoading = true
    private(set) var error: String?
    private(set) var isStopping = false
    private let api: APIClient
    private let server = PlayServerClient()
    let preferences: PlaybackPreferences
    private let subtitleSelection = PlayerSubtitleSelection()
    private var mediaSession: PlaySession?
    var playbackDecision: TranscodeDecision? { mediaSession?.decision }
    private var worker: Task<Void, Never>?
    private var heartbeat: Task<Void, Never>?
    private var needsRestart = false
    private(set) var forceTranscode = false
    private var compatibilityFallback = false
    private var resumePosition = 0.0

    init(target: PlaybackTarget, api: APIClient) {
        self.target = target
        self.api = api
        preferences = PlaybackPreferences(api: api, seriesPath: target.episode == nil ? nil : target.reference.path)
        player.appliesMediaSelectionCriteriaAutomatically = false
    }

    var duration: Double {
        let duration = player.currentItem?.duration.seconds ?? 0
        return duration.isFinite && duration > 0 ? duration : candidates[safe: selectedSource]?.source.duration ?? 0
    }

    func start() {
        guard worker == nil else { return }
        worker = Task { await run() }
    }

    private func run() async {
        do {
            let watched: Watched = try await api.get("\(target.path)/watched")
            resumePosition = target.fromBeginning ? 0 : Double(watched.position)
            progress = PlaybackProgress(api: api, path: target.path, start: resumePosition)
            let requests: [PlayRequest] = try await api.get("\(target.path)/play-servers")
            candidates = try await server.sources(for: requests)
            try Task.checkCancellation()
            try await PlaybackAudioSession.shared.activate()
            let capabilities = PlaybackCapabilities.current(maxBitrate: preferences.maxBitrate, hdrEnabled: preferences.hdrEnabled)
            selectedSource = PlaybackSourceSelection.preferredIndex(in: candidates, capabilities: capabilities) ?? 0
            if target.episode != nil {
                await preferences.load()
                await loadNextEpisode()
            }
            chooseAudio()
            try await openMedia()
            while !Task.isCancelled {
                try await Task.sleep(for: .seconds(1))
                if needsRestart {
                    needsRestart = false
                    resumePosition = currentPosition
                    try await openMedia()
                }
                if player.currentItem?.status == .failed {
                    guard !compatibilityFallback else { throw APIError.message("This video could not be played.") }
                    compatibilityFallback = true
                    resumePosition = currentPosition
                    try await openMedia()
                }
                progress?.record(position: currentPosition, duration: duration)
            }
        } catch is CancellationError {
        } catch let error as URLError where error.code == .cancelled {
        } catch {
            self.error = error.localizedDescription
            isLoading = false
            player.pause()
            await closeMedia()
            await PlaybackAudioSession.shared.deactivate()
        }
    }

    private func openMedia() async throws {
        isLoading = true
        player.pause()
        player.replaceCurrentItem(with: nil)
        await closeMedia()
        try Task.checkCancellation()
        let candidate = candidates[selectedSource]
        let audio = candidate.source.audio.first { $0.key == audioKey }
        let subtitle = preferences.subtitlesOff ? nil : PlaybackLanguages.subtitle(
            in: candidate.source, saved: preferences.subtitleKey, audio: audio)
        mediaSession = try await server.open(candidate,
                                             capabilities: .current(maxBitrate: preferences.maxBitrate, hdrEnabled: preferences.hdrEnabled),
                                             audioKey: audioKey, subtitleKey: subtitle?.key,
                                             forceTranscode: forceTranscode || compatibilityFallback,
                                             compatibilityFallback: compatibilityFallback)
        guard let mediaSession else { throw APIError.invalidResponse }
        try Task.checkCancellation()
        startHeartbeat(mediaSession)
        let item = AVPlayerItem(url: mediaSession.hlsURL)
        item.externalMetadata = PlayerMetadata.items(title: target.title, subtitle: target.episode?.label)
        replacePlayer(with: item)
        let deadline = Date().addingTimeInterval(45)
        while item.status == .unknown && Date() < deadline {
            try await Task.sleep(for: .milliseconds(200))
        }
        guard item.status == .readyToPlay else {
            if !compatibilityFallback {
                compatibilityFallback = true
                try await openMedia()
                return
            }
            throw APIError.message("The video did not become ready. Try another source or check the play server.")
        }
        try Task.checkCancellation()
        // The server muxes our requested track into this HLS session. Automatic
        // selection is disabled, so explicitly enable that session's audio.
        if let group = try await item.asset.loadMediaSelectionGroup(for: .audible),
           let option = group.defaultOption ?? group.options.first {
            item.select(option, in: group)
        }
        try await subtitleSelection.apply(to: item, streams: candidate.source.subtitles, selected: subtitle) { [weak self] key in
            self?.preferences.saveSubtitle(key)
        }
        if resumePosition > 0 {
            await player.seek(to: CMTime(seconds: resumePosition, preferredTimescale: 600),
                              toleranceBefore: .zero, toleranceAfter: .zero)
        }
        try Task.checkCancellation()
        isLoading = false
        player.play()
    }

    func replacePlayer(with item: AVPlayerItem) {
        player.pause()
        player.replaceCurrentItem(with: nil)
        // A new server session can change audio codec/channel layout. Start a
        // fresh playback pipeline, as when leaving and reopening the title.
        let replacement = AVPlayer(playerItem: item)
        replacement.appliesMediaSelectionCriteriaAutomatically = false
        player = replacement
    }

    func selectSource(_ index: Int) {
        guard !isLoading, candidates.indices.contains(index), index != selectedSource else { return }
        selectedSource = index
        compatibilityFallback = false
        chooseAudio()
        needsRestart = true
    }

    func selectAudio(_ key: String) {
        guard !isLoading, key != audioKey else { return }
        audioKey = key
        preferences.saveAudio(key)
        needsRestart = true
    }

    func selectBitrate(_ bitrate: Int) {
        guard !isLoading, bitrate != preferences.maxBitrate, PlaybackQuality.options.contains(bitrate) else { return }
        preferences.saveBitrate(bitrate)
        needsRestart = true
    }

    func setHDR(_ enabled: Bool) {
        guard !isLoading, preferences.hdrEnabled != enabled else { return }
        preferences.saveHDR(enabled)
        compatibilityFallback = false
        needsRestart = true
    }

    func setForceTranscode(_ enabled: Bool) {
        guard !isLoading, forceTranscode != enabled else { return }
        forceTranscode = enabled
        compatibilityFallback = false
        needsRestart = true
    }

    private func chooseAudio() {
        audioKey = PlaybackLanguages.audio(in: candidates[selectedSource].source, saved: preferences.audioKey)?.key
    }

    private var currentPosition: Double {
        let seconds = player.currentTime().seconds
        return seconds.isFinite ? seconds : resumePosition
    }

    func finishPlayback() { progress?.finish() }

    private func loadNextEpisode() async {
        guard let episode = target.episode else { return }
        // Next-up is optional; failure here must not prevent playing the selected episode.
        do {
            let path = "\(target.reference.path)/episodes/\(episode.number + 1)"
            let next: Episode = try await api.get(path)
            let requests: [PlayRequest] = try await api.get("\(path)/play-servers")
            _ = try await server.sources(for: requests)
            nextEpisode = next
        } catch {
            nextEpisode = nil
        }
    }

    private func startHeartbeat(_ media: PlaySession) {
        heartbeat = Task {
            var failures = 0
            while !Task.isCancelled {
                do {
                    try await Task.sleep(for: .seconds(5))
                    try await server.keepAlive(media)
                    failures = 0
                } catch is CancellationError { return }
                catch {
                    if Task.isCancelled { return }
                    failures += 1
                    if failures >= 3 || (error as? APIError)?.statusCode == 404 {
                        self.error = "The play-server session was lost. Retry to reconnect."
                        player.pause()
                        worker?.cancel()
                        return
                    }
                }
            }
        }
    }

    private func closeMedia() async {
        subtitleSelection.detach()
        heartbeat?.cancel()
        heartbeat = nil
        if let media = mediaSession {
            mediaSession = nil
            await server.close(media)
        }
    }

    func stop() async {
        guard !isStopping else { return }
        isStopping = true
        player.pause()
        worker?.cancel()
        await worker?.value
        await progress?.flush()
        NotificationCenter.default.post(name: .watchHistoryDidChange, object: nil)
        await preferences.flush()
        await closeMedia()
        player.replaceCurrentItem(with: nil)
        await PlaybackAudioSession.shared.deactivate()
    }
}

private extension Array {
    subscript(safe index: Int) -> Element? { indices.contains(index) ? self[index] : nil }
}
