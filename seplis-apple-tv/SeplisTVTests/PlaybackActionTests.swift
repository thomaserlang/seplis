import XCTest
@testable import seplis_apple_tv

nonisolated final class PlaybackActionTests: XCTestCase {
    func testStandardPlaybackActions() {
        let unwatched = Watched(times: 0, position: 0)
        let inProgress = Watched(times: 0, position: 120)
        let completed = Watched(times: 1, position: 0)

        XCTAssertEqual(PlaybackAction(watched: unwatched), .play)
        XCTAssertEqual(PlaybackAction(watched: inProgress), .resume)
        XCTAssertEqual(PlaybackAction(watched: completed), .play)
        XCTAssertEqual(PlaybackAction(watched: completed, rewatchCompleted: true), .rewatch)
        XCTAssertEqual(PlaybackAction(watched: Watched(times: 1, position: 120), rewatchCompleted: true), .resume)
        XCTAssertEqual(PlaybackAction.rewatch.title, "Rewatch")
        XCTAssertEqual(PlaybackAction.resume.title, "Resume")
        XCTAssertEqual(PlaybackAction.play.title, "Play")
        XCTAssertTrue(PlaybackAction.play.fromBeginning)
        XCTAssertFalse(PlaybackAction.resume.fromBeginning)
        XCTAssertTrue(PlaybackAction.rewatch.fromBeginning)
    }
}
