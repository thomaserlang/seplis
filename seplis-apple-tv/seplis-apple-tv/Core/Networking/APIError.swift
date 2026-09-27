import Foundation

nonisolated enum APIError: LocalizedError {
    case invalidResponse
    case http(Int, Data)
    case message(String)

    var statusCode: Int? {
        if case .http(let status, _) = self { return status }
        return nil
    }

    var errorDescription: String? {
        switch self {
        case .invalidResponse: return "The server returned an invalid response."
        case .message(let message): return message
        case .http(let status, _):
            switch status {
            case 401: return "Your session has expired. Sign in again."
            case 403: return "You do not have access to this item."
            case 404: return "This item is no longer available."
            case 410: return "This code has expired. Request a new code."
            case 429: return "Too many requests. Please try again shortly."
            default: return "The server could not complete the request (\(status))."
            }
        }
    }
}
