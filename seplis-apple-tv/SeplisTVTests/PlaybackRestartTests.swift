import AVFoundation
import XCTest
@testable import seplis_apple_tv

nonisolated final class PlaybackRestartTests: XCTestCase {
    @MainActor func testEachStreamReplacementDetachesOldAudioPipeline() {
        let target = PlaybackTarget(reference: .init(kind: .movie, id: 1), title: "Test", episode: nil, fromBeginning: false)
        let model = PlaybackModel(target: target, api: APIClient())
        for _ in 0..<3 {
            let previous = model.player
            let item = AVPlayerItem(asset: AVMutableComposition())
            model.replacePlayer(with: item)
            XCTAssertFalse(model.player === previous)
            XCTAssertNil(previous.currentItem)
            XCTAssertTrue(model.player.currentItem === item)
            XCTAssertFalse(model.player.appliesMediaSelectionCriteriaAutomatically)
            XCTAssertFalse(model.player.isMuted)
        }
    }
}
