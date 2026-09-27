import Foundation
import Observation

@MainActor @Observable
final class PlaybackPreferences {
    var error: String?
    private(set) var maxBitrate: Int
    private(set) var hdrEnabled: Bool
    private var series: SeriesPlaybackSettings?
    private let api: APIClient
    private let seriesPath: String?
    private let defaults: UserDefaults
    private let prefix: String
    private var pendingSave: Task<Void, Never>?

    init(api: APIClient, seriesPath: String?, defaults: UserDefaults = .standard) {
        self.api = api
        self.seriesPath = seriesPath
        self.defaults = defaults
        prefix = "playback.\(api.accountID.map(String.init) ?? "guest")."
        let saved = defaults.integer(forKey: prefix + "maxBitrate")
        maxBitrate = PlaybackQuality.options.contains(saved) ? saved : PlaybackQuality.defaultBitrate
        hdrEnabled = defaults.object(forKey: prefix + "hdrEnabled") as? Bool ?? true
    }

    var audioKey: String? { series?.audioLang ?? defaults.string(forKey: prefix + "audio") }
    var subtitleKey: String? { series?.subtitleLang ?? defaults.string(forKey: prefix + "subtitle") }
    var subtitlesOff: Bool { series?.subtitleLang == nil && defaults.bool(forKey: prefix + "subtitlesOff") }

    func load() async {
        guard let seriesPath else { return }
        do { series = try await api.get("\(seriesPath)/user-settings") } catch {
            self.error = "Series playback preferences could not be loaded. Using this profile's saved defaults."
        }
    }

    func saveAudio(_ key: String) {
        defaults.set(key, forKey: prefix + "audio")
        series = SeriesPlaybackSettings(audioLang: key, subtitleLang: series?.subtitleLang)
        save(field: "audio_lang", value: key)
    }

    func saveBitrate(_ bitrate: Int) {
        guard PlaybackQuality.options.contains(bitrate) else { return }
        maxBitrate = bitrate
        defaults.set(bitrate, forKey: prefix + "maxBitrate")
    }

    func saveHDR(_ enabled: Bool) {
        hdrEnabled = enabled
        defaults.set(enabled, forKey: prefix + "hdrEnabled")
    }

    func saveSubtitle(_ key: String?) {
        defaults.set(key, forKey: prefix + "subtitle")
        defaults.set(key == nil, forKey: prefix + "subtitlesOff")
        series = SeriesPlaybackSettings(audioLang: series?.audioLang, subtitleLang: key)
        save(field: "subtitle_lang", value: key)
    }

    private func save(field: String, value: String?) {
        guard let seriesPath else { return }
        let previous = pendingSave
        pendingSave = Task {
            await previous?.value
            do {
                let body = try JSONSerialization.data(withJSONObject: [field: value as Any? ?? NSNull()])
                try await api.perform("\(seriesPath)/user-settings", method: "PUT", body: body)
            } catch {
                self.error = "Playback preferences were saved on this Apple TV but could not be synced to Seplis."
            }
        }
    }

    func flush() async { await pendingSave?.value }
}

nonisolated struct SeriesPlaybackSettings: Decodable {
    let audioLang: String?
    let subtitleLang: String?
}
