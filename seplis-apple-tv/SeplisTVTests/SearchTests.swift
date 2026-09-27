import XCTest
@testable import seplis_apple_tv

nonisolated final class SearchTests: XCTestCase {
    @MainActor func testSearchUsesSearchEndpointAndClearsBlankQuery() async {
        let transport = stubSession { request in
            XCTAssertEqual(request.url?.path, "/2/search")
            XCTAssertTrue(URLComponents(url: request.url!, resolvingAgainstBaseURL: false)!.queryItems!.contains(.init(name: "query", value: "treasure")))
            XCTAssertTrue(URLComponents(url: request.url!, resolvingAgainstBaseURL: false)!.queryItems!.contains(.init(name: "limit", value: "60")))
            return (200, Data("[{\"type\":\"movie\",\"id\":1,\"title\":\"National Treasure\"}]".utf8))
        }
        let model = SearchModel()
        let api = APIClient(session: transport)
        await model.search(" treasure ", api: api)
        XCTAssertEqual(model.results.first?.id, 1)
        await model.search(" ", api: api)
        XCTAssertTrue(model.results.isEmpty)
        XCTAssertFalse(model.isLoading)
    }
}
