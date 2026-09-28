import XCTest
@testable import seplis_apple_tv

nonisolated final class SeriesDetailTests: XCTestCase {
    @MainActor func testDetailFields() throws {
        let series = try APIClient.decoder().decode(Series.self, from: Data(#"{"id":2,"title":"Show","premiered":"2001-01-01","ended":"2011-01-01","runtime":43,"language":"en","rating":7.5,"total_episodes":217,"seasons":[{"season":1,"total":10},{"season":2,"total":10}],"status":2}"#.utf8))
        XCTAssertEqual(series.detailFacts.map(\.value), ["2001-2011", "Ended", "43 min", "English", "★ 7.5", "2", "217"])
        XCTAssertEqual(series.statusLabel, "Ended")
    }
}
