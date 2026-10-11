import Synchronization
import XCTest
@testable import seplis_apple_tv

nonisolated final class EpisodeTests: XCTestCase {
    @MainActor func testEpisodeHeadingAndAirDateMatchWeb() throws {
        for position in [0, 120] {
            let episode = try APIClient.decoder().decode(Episode.self, from: Data("""
            {"number":2,"air_date":"2003-09-30","user_watched":{"times":0,"position":\(position)}}
            """.utf8))
            XCTAssertEqual(episode.airDate, "2003-09-30")
            XCTAssertEqual(episode.formattedAirDate(locale: Locale(identifier: "en_US"),
                                                    timeZone: TimeZone(secondsFromGMT: 0)!), "Sep 30, 2003")
            XCTAssertEqual(episode.watchHeading, position == 0 ? "Next to watch" : "Continue watching")
        }
        let episode = try APIClient.decoder().decode(Episode.self, from: Data(#"{"number":2}"#.utf8))
        XCTAssertNil(episode.airDate)
        XCTAssertEqual(episode.watchHeading, "Next to watch")
    }

    @MainActor func testSeasonWatchedUsesAbsoluteEpisodeNumberAndReloads() async throws {
        let methods = Mutex<[String]>([])
        let transport = stubSession { request in
            methods.withLock { $0.append("\(request.httpMethod!) \(request.url!.path)") }
            guard request.httpMethod == "GET" else { return (204, Data()) }
            let query = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)!.queryItems!
            XCTAssertTrue(query.contains(.init(name: "season", value: "2")))
            XCTAssertTrue(query.contains(.init(name: "expand", value: "user_watched,user_can_watch")))
            return (200, Data(#"{"records":[],"cursor":null}"#.utf8))
        }
        let episode = try JSONDecoder().decode(Episode.self, from: Data(#"{"number":25,"season":2,"episode":1}"#.utf8))
        let model = EpisodesModel()
        let api = APIClient(session: transport)
        let reference = MediaReference(kind: .series, id: 1)
        await model.changeWatched(reference: reference, episode: episode, increment: true, season: 2, api: api)
        await model.changeWatched(reference: reference, episode: episode, increment: false, season: 2, api: api)
        XCTAssertEqual(methods.withLock { $0 }, [
            "POST /2/series/1/episodes/25/watched", "GET /2/series/1/episodes",
            "DELETE /2/series/1/episodes/25/watched", "GET /2/series/1/episodes",
        ])
        XCTAssertNil(model.updateError)
        XCTAssertFalse(model.isUpdating)
    }
}
