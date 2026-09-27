import Foundation

nonisolated struct TopShelfSnapshot: Codable {
    let accountID: Int
    var items: [TopShelfEntry]
}

nonisolated struct TopShelfEntry: Codable {
    let mediaID: Int
    let kind: String
    let title: String
    let imageURL: URL
    let episodeNumber: Int?
    let progress: Double

    var identifier: String { "\(kind)-\(mediaID)" }
}

nonisolated struct TopShelfStore {
    static let groupID = "group.net.seplis.tv"
    private let fileURL: URL?

    init(directory: URL? = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: groupID)) {
        fileURL = directory?.appendingPathComponent("top-shelf.json")
    }

    func load() -> TopShelfSnapshot? {
        guard let fileURL, let data = try? Data(contentsOf: fileURL) else { return nil }
        return try? JSONDecoder().decode(TopShelfSnapshot.self, from: data)
    }

    func save(_ snapshot: TopShelfSnapshot?) throws {
        guard let fileURL else { return }
        guard let snapshot else {
            if FileManager.default.fileExists(atPath: fileURL.path) {
                try FileManager.default.removeItem(at: fileURL)
            }
            return
        }
        try JSONEncoder().encode(snapshot).write(to: fileURL, options: .atomic)
    }
}
