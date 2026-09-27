import AVFoundation

@MainActor
final class PlayerSubtitleSelection {
    private var observation: (any NSObjectProtocol)?
    private weak var item: AVPlayerItem?
    private var group: AVMediaSelectionGroup?
    private var previous: AVMediaSelectionOption?
    private var streams: [PlayStream] = []
    private var onChange: (@MainActor (String?) -> Void)?

    func apply(
        to item: AVPlayerItem, streams: [PlayStream], selected: PlayStream?,
        onChange: @escaping @MainActor (String?) -> Void
    ) async throws {
        detach()
        guard let group = try await item.asset.loadMediaSelectionGroup(for: .legible) else { return }
        let option = selected.flatMap { stream in
            closestOption(to: stream, in: group.options)
        }
        self.item = item
        self.group = group
        self.streams = streams
        self.onChange = onChange
        previous = option
        item.select(option, in: group)
        observation = NotificationCenter.default.addObserver(
            forName: AVPlayerItem.mediaSelectionDidChangeNotification, object: item, queue: .main
        ) { [weak self] _ in
            MainActor.assumeIsolated { self?.selectionChanged() }
        }
    }

    private func selectionChanged() {
        guard let item, let group else { return }
        let current = item.currentMediaSelection.selectedMediaOption(in: group)
        guard current != previous else { return }
        previous = current
        guard let current else {
            onChange?(nil)
            return
        }
        let index = group.options.firstIndex(of: current) ?? 0
        let matching = streams.filter {
            PlaybackLanguages.matches(current.extendedLanguageTag ?? current.locale?.identifier ?? "", $0.language)
        }
        guard let stream = matching.min(by: { abs(($0.groupIndex ?? 0) - index) < abs(($1.groupIndex ?? 0) - index) })
        else { return }
        onChange?(stream.key)
    }

    private func closestOption(to stream: PlayStream, in options: [AVMediaSelectionOption]) -> AVMediaSelectionOption? {
        let matches = options.enumerated().filter {
            PlaybackLanguages.matches(
                $0.element.extendedLanguageTag ?? $0.element.locale?.identifier ?? "", stream.language)
        }
        return matches.min {
            abs($0.offset - (stream.groupIndex ?? 0)) < abs($1.offset - (stream.groupIndex ?? 0))
        }?.element
    }

    func detach() {
        if let observation { NotificationCenter.default.removeObserver(observation) }
        observation = nil
        item = nil
        group = nil
        previous = nil
        onChange = nil
        streams = []
    }
}
