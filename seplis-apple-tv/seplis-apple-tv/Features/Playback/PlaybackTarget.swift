import Foundation

nonisolated struct PlaybackTarget: Identifiable {
    let id = UUID()
    let reference: MediaReference
    let title: String
    let episode: Episode?
    let fromBeginning: Bool

    var path: String {
        if let episode { "\(reference.path)/episodes/\(episode.number)" } else { reference.path }
    }
}
