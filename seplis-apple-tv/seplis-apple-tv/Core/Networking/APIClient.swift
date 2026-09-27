import Foundation

@MainActor
final class APIClient {
    static let productionURL = URL(string: "https://api.seplis.net/2/")!

    let baseURL: URL
    var accountID: Int?
    private let token: String?
    private let session: URLSession
    var onUnauthorized: (() -> Void)?

    init(baseURL: URL = productionURL, token: String? = nil, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.token = token
        self.session = session
    }

    func get<T: Decodable>(_ path: String, query: [URLQueryItem] = []) async throws -> T {
        try await send(path, query: query)
    }

    func getOptional<T: Decodable>(_ path: String) async throws -> T? {
        let data = try await request(path)
        return data.isEmpty ? nil : try Self.decoder().decode(T?.self, from: data)
    }

    func send<T: Decodable>(
        _ path: String, method: String = "GET", query: [URLQueryItem] = [], body: Data? = nil
    ) async throws -> T {
        let data = try await request(path, method: method, query: query, body: body)
        return try Self.decoder().decode(T.self, from: data)
    }

    func perform(_ path: String, method: String, body: Data? = nil) async throws {
        _ = try await request(path, method: method, body: body)
    }

    private func request(
        _ path: String, method: String = "GET", query: [URLQueryItem] = [], body: Data? = nil
    ) async throws -> Data {
        var request = URLRequest(url: baseURL.appending(path: path).addingQuery(query))
        request.httpMethod = method
        request.httpBody = body
        request.timeoutInterval = 30
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if body != nil { request.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        if let token { request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization") }
        let (data, response) = try await session.data(for: request)
        guard let response = response as? HTTPURLResponse else { throw APIError.invalidResponse }
        guard (200..<300).contains(response.statusCode) else {
            if response.statusCode == 401, token != nil { onUnauthorized?() }
            throw APIError.http(response.statusCode, data)
        }
        return data
    }

    static func body<T: Encodable>(_ value: T) throws -> Data {
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        return try encoder.encode(value)
    }

    static func decoder() -> JSONDecoder {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .custom { decoder in
            let value = try decoder.singleValueContainer().decode(String.self)
            let formatter = ISO8601DateFormatter()
            formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            if let date = formatter.date(from: value) { return date }
            formatter.formatOptions = [.withInternetDateTime]
            guard let date = formatter.date(from: value) else {
                throw DecodingError.dataCorrupted(.init(codingPath: decoder.codingPath,
                                                        debugDescription: "Invalid API date"))
            }
            return date
        }
        return decoder
    }
}

extension URL {
    func addingQuery(_ items: [URLQueryItem]) -> URL {
        guard !items.isEmpty, var parts = URLComponents(url: self, resolvingAgainstBaseURL: true) else {
            return self
        }
        parts.queryItems = (parts.queryItems ?? []) + items
        return parts.url ?? self
    }
}
