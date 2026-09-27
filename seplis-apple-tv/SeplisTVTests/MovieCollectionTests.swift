import Synchronization
import XCTest
@testable import seplis_apple_tv

nonisolated final class MovieCollectionTests: XCTestCase {
    @MainActor func testCollectionUsesReleaseOrderAndPaginates() async {
        let requests = Mutex(0)
        let transport = stubSession { request in
            requests.withLock { $0 += 1 }
            XCTAssertEqual(request.url?.path, "/2/movies")
            let query = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)!.queryItems!
            XCTAssertTrue(query.contains(.init(name: "collection_id", value: "7")))
            XCTAssertTrue(query.contains(.init(name: "sort", value: "release_date_asc")))
            XCTAssertFalse(query.contains { $0.name == "user_can_watch" })
            let more = query.contains(.init(name: "cursor", value: "next"))
            let json = more ? #"{"records":[{"id":1},{"id":2}],"cursor":null}"#
                : #"{"records":[{"id":1}],"cursor":"next"}"#
            return (200, Data(json.utf8))
        }
        let model = MovieCollectionModel()
        let api = APIClient(session: transport)
        await model.load(collectionID: 7, api: api)
        await model.load(collectionID: 7, api: api, more: true)
        await model.load(collectionID: 7, api: api, more: true)
        XCTAssertEqual(model.movies.map(\.id), [1, 2])
        XCTAssertEqual(requests.withLock { $0 }, 2)
        XCTAssertTrue(model.hasLoaded)
        XCTAssertNil(model.error)
    }
}
