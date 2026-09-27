import XCTest
@testable import seplis_apple_tv

nonisolated final class CatalogTests: XCTestCase {
    @MainActor func testAvailableIsDefaultAndCanBeCleared() {
        var filters = CatalogFilters()
        for kind in [MediaKind.series, .movie] {
            XCTAssertTrue(filters.query(kind: kind).contains(.init(name: "user_can_watch", value: "true")))
        }
        filters.available = .any
        for kind in [MediaKind.series, .movie] {
            XCTAssertFalse(filters.query(kind: kind).contains { $0.name == "user_can_watch" })
        }
    }

    @MainActor func testFilterQueryMatchesWebContract() {
        var filters = CatalogFilters()
        filters.available = .yes
        filters.watched = .no
        filters.genres = [1: .yes, 2: .no]
        filters.languages = ["en", "da"]
        filters.yearFrom = "2001"
        filters.yearTo = "2020"
        filters.ratingFrom = "7.5"
        let query = filters.query(kind: .series)
        for item in [URLQueryItem(name: "user_can_watch", value: "true"),
                     .init(name: "user_has_watched", value: "false"),
                     .init(name: "genre_id", value: "1"), .init(name: "not_genre_id", value: "2"),
                     .init(name: "premiered_gt", value: "2001-01-01"), .init(name: "rating_gt", value: "7.5")] {
            XCTAssertTrue(query.contains(item))
        }
        XCTAssertFalse(query.contains { $0.name == "user_watchlist" })
        XCTAssertTrue(filters.query(kind: .movie).contains(.init(name: "release_date_lt", value: "2020-12-31")))
        XCTAssertNil(filters.validationError)
        filters.ratingTo = "2"
        XCTAssertNotNil(filters.validationError)
    }

    @MainActor func testCatalogPaginationDeduplicatesAndResets() async {
        let transport = stubSession { request in
            let more = URLComponents(url: request.url!, resolvingAgainstBaseURL: false)?.queryItems?.contains { $0.name == "cursor" } == true
            return (200, Data((more ? "{\"records\":[{\"id\":1},{\"id\":2}],\"cursor\":null}" :
                "{\"records\":[{\"id\":1}],\"cursor\":\"next\"}").utf8))
        }
        let model = CatalogModel()
        let api = APIClient(session: transport)
        await model.load(api: api, kind: .movie, filters: CatalogFilters())
        await model.load(api: api, kind: .movie, filters: CatalogFilters(), more: true)
        XCTAssertEqual(model.items.map(\.id), [1, 2])
        XCTAssertNil(model.cursor)
        await model.load(api: api, kind: .series, filters: CatalogFilters())
        XCTAssertEqual(model.items.map(\.id), [1])
    }
}
