nonisolated enum PlaybackAction: Equatable {
    case play
    case resume
    case rewatch

    init(watched: Watched?, rewatchCompleted: Bool = false) {
        if (watched?.position ?? 0) > 0 {
            self = .resume
        } else if rewatchCompleted && (watched?.times ?? 0) > 0 {
            self = .rewatch
        } else {
            self = .play
        }
    }

    var title: String {
        switch self {
        case .play: "Play"
        case .resume: "Resume"
        case .rewatch: "Rewatch"
        }
    }

    var systemImage: String { self == .rewatch ? "arrow.counterclockwise" : "play.fill" }
    var fromBeginning: Bool { self != .resume }
}
