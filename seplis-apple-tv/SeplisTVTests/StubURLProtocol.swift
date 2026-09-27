import Foundation
import Synchronization
import XCTest
@testable import seplis_apple_tv

nonisolated final class StubURLProtocol: URLProtocol, @unchecked Sendable {
    typealias Handler = @Sendable (URLRequest) throws -> (Int, Data)
    static let handler = Mutex<Handler?>(nil)
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        do {
            let callback = Self.handler.withLock { $0 }
            let (status, data) = try callback!(request)
            let response = HTTPURLResponse(url: request.url!, statusCode: status, httpVersion: nil, headerFields: nil)!
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch { client?.urlProtocol(self, didFailWithError: error) }
    }
    override func stopLoading() {}
}

func stubSession(_ handler: @escaping StubURLProtocol.Handler) -> URLSession {
    StubURLProtocol.handler.withLock { $0 = handler }
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [StubURLProtocol.self]
    return URLSession(configuration: config)
}

final class MemoryProfileStore: ProfileStore {
    var snapshot = ProfileSnapshot()
    var failure = false
    var loadFailure = false
    func load() throws -> ProfileSnapshot {
        if loadFailure { throw APIError.message("Storage unavailable") }
        return snapshot
    }
    func save(_ snapshot: ProfileSnapshot) throws {
        if failure { throw APIError.message("Storage unavailable") }
        self.snapshot = snapshot
    }
}
