import Foundation
import OSLog
import TVServices

extension Notification.Name {
    static let watchHistoryDidChange = Notification.Name("watchHistoryDidChange")
}

@MainActor
final class TopShelfPublisher {
    private let store: TopShelfStore
    private let contentDidChange: () -> Void
    private var api: APIClient?
    private(set) var refreshTask: Task<Void, Never>?
    private let logger = Logger(subsystem: "net.seplis.tv", category: "TopShelf")

    init(store: TopShelfStore = TopShelfStore(),
         contentDidChange: @escaping () -> Void = { TVTopShelfContentProvider.topShelfContentDidChange() }) {
        self.store = store
        self.contentDidChange = contentDidChange
    }

    func configure(api: APIClient?) {
        refreshTask?.cancel()
        self.api = api
        if store.load()?.accountID != api?.accountID || api == nil {
            publish(nil)
        }
        refresh()
    }

    func refresh() {
        refreshTask?.cancel()
        guard let api, let accountID = api.accountID else { return }
        refreshTask = Task {
            do {
                try await Task.sleep(for: .milliseconds(300))
                let page: Page<WatchedRecord> = try await api.get("users/me/watched", query: [
                    .init(name: "user_can_watch", value: "true"),
                ])
                var items: [TopShelfEntry] = []
                for record in page.records {
                    try Task.checkCancellation()
                    if let item = try await Self.entry(for: record, api: api) { items.append(item) }
                    if items.count == 12 { break }
                }
                try Task.checkCancellation()
                guard self.api === api else { return }
                publish(TopShelfSnapshot(accountID: accountID, items: items))
            } catch is CancellationError {
            } catch let error as URLError where error.code == .cancelled {
            } catch {
                logger.error("Could not refresh Top Shelf: \(error.localizedDescription)")
            }
        }
    }

    private static func entry(for record: WatchedRecord, api: APIClient) async throws -> TopShelfEntry? {
        let media = record.data
        guard let poster = media.posterImage,
              let imageURL = URL(string: "\(poster.url)@SX640.webp") else { return nil }
        let reference = MediaReference(kind: record.type, id: media.id)
        let episode: Episode?
        let position: Int
        if record.type == .series {
            episode = try await api.getOptional("\(reference.path)/episode-to-watch")
            guard let episode, episode.canPlay else { return nil }
            position = episode.userWatched?.position ?? 0
        } else {
            episode = nil
            let watched: Watched = try await api.get("\(reference.path)/watched")
            guard watched.position > 0 else { return nil }
            position = watched.position
        }
        let runtime = episode?.runtime ?? media.runtime ?? 0
        let progress = runtime > 0 ? min(1, Double(position) / Double(runtime * 60)) : 0
        return TopShelfEntry(mediaID: media.id, kind: record.type.rawValue,
                             title: episode.map { "\(media.displayTitle) - \($0.numberLabel)" } ?? media.displayTitle,
                             imageURL: imageURL, episodeNumber: episode?.number, progress: progress)
    }

    private func publish(_ snapshot: TopShelfSnapshot?) {
        do {
            try store.save(snapshot)
            contentDidChange()
        } catch {
            logger.error("Could not save Top Shelf: \(error.localizedDescription)")
        }
    }
}
