import Observation
import Synchronization
import XCTest
@testable import seplis_apple_tv

nonisolated final class MovieDetailTests: XCTestCase {
    @MainActor func testDetailFields() throws {
        let movie = try APIClient.decoder().decode(Movie.self, from: Data(#"{"id":1,"title":"Treasure","release_date":"2004-11-19","runtime":131,"language":"en","rating":6.9,"budget":100000000,"revenue":348000000,"status":1}"#.utf8))
        XCTAssertEqual(movie.detailFacts.map(\.value), ["2004", "2h 11m", "English", "★ 6.9", "$100M", "$348M"])
        XCTAssertEqual(movie.statusLabel, "Released")
    }

    @MainActor func testMovieRefreshKeepsPlayAvailableUntilResponseArrives() async {
        let transport = stubSession { request in
            let response = request.url?.path.hasSuffix("/play-servers") == true
                ? #"[{"play_id":"test","play_url":"https://play.example.test"}]"# : #"{"id":1}"#
            return (200, Data(response.utf8))
        }
        let model = MovieDetailModel(reference: .init(kind: .movie, id: 1), api: APIClient(session: transport))
        await model.load()
        XCTAssertTrue(model.canPlay)
        let availabilityChanged = Mutex(false)
        withObservationTracking {
            _ = model.canPlay
        } onChange: {
            availabilityChanged.withLock { $0 = true }
        }
        await model.load()
        XCTAssertTrue(model.canPlay)
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
            let model = MovieDetailModel(reference: .init(kind: .movie, id: 1), api: APIClient(session: transport))
            await model.load()
            XCTAssertNil(model.error)
            XCTAssertEqual(model.canPlay, available)
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
        let model = MovieDetailModel(reference: .init(kind: .movie, id: 1), api: APIClient(session: transport))
        await model.changeWatched(increment: true)
        await model.changeWatched(increment: false)
        XCTAssertEqual(methods.withLock { $0 }, ["POST /2/movies/1/watched", "DELETE /2/movies/1/watched"])
    }
}
