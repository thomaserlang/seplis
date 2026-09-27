import Observation
import Synchronization
import XCTest
@testable import seplis_apple_tv

nonisolated final class MediaDetailTests: XCTestCase {
    @MainActor func testMovieRefreshKeepsPlayAvailableUntilResponseArrives() async {
        let transport = stubSession { request in
            let response = request.url?.path.hasSuffix("/play-servers") == true
                ? #"[{"play_id":"test","play_url":"https://play.example.test"}]"# : #"{"id":1}"#
            return (200, Data(response.utf8))
        }
        let model = MediaDetailModel(reference: .init(kind: .movie, id: 1), api: APIClient(session: transport))
        await model.load()
        XCTAssertTrue(model.canPlayMovie)
        let availabilityChanged = Mutex(false)
        withObservationTracking {
            _ = model.canPlayMovie
        } onChange: {
            availabilityChanged.withLock { $0 = true }
        }
        await model.load()
        XCTAssertTrue(model.canPlayMovie)
        XCTAssertFalse(availabilityChanged.withLock { $0 }, "Refreshing must not temporarily disable the focused Play button")
    }

    @MainActor func testMovieDetailLoadsAvailability() async {
        for available in [true, false] {
            let transport = stubSession { request in
                if request.url?.path == "/2/movies/1/play-servers" {
                    let response = available ? #"[{"play_id":"test","play_url":"https://play.example.test"}]"# : "[]"
                    return (200, Data(response.utf8))
                }
                XCTAssertEqual(request.url?.path, "/2/movies/1")
                let query = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)!.queryItems!
                let expand = query.first { $0.name == "expand" }?.value?.split(separator: ",")
                XCTAssertFalse(expand?.contains("user_can_watch") == true)
                return (200, Data(#"{"id":1}"#.utf8))
            }
            let model = MediaDetailModel(reference: .init(kind: .movie, id: 1), api: APIClient(session: transport))
            await model.load()
            XCTAssertNil(model.error)
            XCTAssertEqual(model.canPlayMovie, available)
        }
    }

    @MainActor func testCounterUsesIncrementAndDecrementEndpoints() async {
        let methods = Mutex<[String]>([])
        let transport = stubSession { request in
            if request.url?.path.hasSuffix("/play-servers") == true {
                return (200, Data("[]".utf8))
            }
            if request.httpMethod != "GET" {
                methods.withLock { $0.append("\(request.httpMethod!) \(request.url!.path)") }
                return (204, Data())
            }
            return (200, Data("{\"id\":1}".utf8))
        }
        let model = MediaDetailModel(reference: .init(kind: .movie, id: 1), api: APIClient(session: transport))
        await model.changeWatched(increment: true)
        await model.changeWatched(increment: false)
        XCTAssertEqual(methods.withLock { $0 }, ["POST /2/movies/1/watched", "DELETE /2/movies/1/watched"])
    }
}
