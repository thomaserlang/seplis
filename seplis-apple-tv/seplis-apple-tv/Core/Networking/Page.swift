import Foundation

nonisolated struct Page<Record: Decodable>: Decodable {
    let records: [Record]
    let cursor: String?
}
