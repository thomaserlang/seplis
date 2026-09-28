import XCTest
@testable import seplis_apple_tv

nonisolated final class CastRowTests: XCTestCase {
    @MainActor func testLoadsMovieAndSeriesCastPages() async {
        let transport = stubSession { request in
            let query = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)?.queryItems ?? []
            let more = query.contains { $0.name == "cursor" }
            let id = more ? 2 : 1
            let cursor = more ? "null" : #""next""#
            let credit = request.url!.path.contains("/movies/")
                ? #""character":"Character \#(id)""#
                : #""roles":[{"character":"Role \#(id)"},{"character":"Alias \#(id)"}]"#
            let response = #"{"records":[{"person":{"id":\#(id),"name":"Actor \#(id)"},\#(credit)}],"cursor":\#(cursor)}"#
            return (200, Data(response.utf8))
        }
        let api = APIClient(session: transport)
        for kind in [MediaKind.movie, .series] {
            let model = CastRowModel()
            let reference = MediaReference(kind: kind, id: 1)
            await model.load(reference: reference, api: api)
            await model.load(reference: reference, api: api, more: true)
            XCTAssertNil(model.error)
            XCTAssertEqual(model.members.map(\.person.name), ["Actor 1", "Actor 2"])
            let expectedRoles = kind == .movie ? ["Character 1"] : ["Role 1", "Alias 1"]
            XCTAssertEqual(model.members.first?.roles, expectedRoles)
            XCTAssertNil(model.cursor)
        }
    }
}
