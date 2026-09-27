import Foundation

enum PlaybackLanguages {
    static func audio(in source: PlaySource, saved: String?, preferredLanguages: [String] = preferred) -> PlayStream? {
        if let match = match(saved, in: source.audio) { return match }
        for language in ["jpn", "eng"] + preferredLanguages {
            if let stream = source.audio.first(where: { matches($0.language, language) }) { return stream }
        }
        return source.audio.first
    }

    static func subtitle(
        in source: PlaySource, saved: String?, audio: PlayStream?, preferredLanguages: [String] = preferred
    ) -> PlayStream? {
        if let match = match(saved, in: source.subtitles) { return match }
        for language in preferredLanguages + ["eng"] {
            if let stream = source.subtitles.first(where: { matches($0.language, language) }) {
                return saved == nil && audio.map { matches(stream.language, $0.language) } == true ? nil : stream
            }
        }
        return source.subtitles.first { stream in
            stream.forced && audio.map { matches(stream.language, $0.language) } == true
        }
    }

    static var preferred: [String] {
        Locale.preferredLanguages.compactMap {
            Locale.Language(identifier: $0).languageCode?.identifier(.alpha3)
        }
    }

    static func matches(_ lhs: String, _ rhs: String) -> Bool {
        func normalized(_ value: String) -> String {
            Locale.Language(identifier: value.lowercased()).languageCode?.identifier(.alpha3) ?? value.lowercased()
        }
        return normalized(lhs) == normalized(rhs)
    }

    private static func match(_ key: String?, in streams: [PlayStream]) -> PlayStream? {
        guard let key else { return nil }
        return streams.first { $0.key == key }
            ?? streams.first { $0.language == key.components(separatedBy: ":")[0] }
    }
}
