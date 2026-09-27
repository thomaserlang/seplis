import Foundation

enum PlayServerFailure {
    static func message(for error: Error) -> String {
        switch error {
        case let error as DecodingError:
            let path: [any CodingKey]
            switch error {
            case .keyNotFound(let key, let context): path = context.codingPath + [key]
            case .typeMismatch(_, let context), .valueNotFound(_, let context), .dataCorrupted(let context):
                path = context.codingPath
            @unknown default: path = []
            }
            let field = path.map(\.stringValue).joined(separator: ".")
            return "The source response has an invalid or missing field\(field.isEmpty ? "" : " (\(field))")."
        case let error as URLError:
            switch error.code {
            case .appTransportSecurityRequiresSecureConnection:
                return "Apple blocked an insecure HTTP connection. The server needs HTTPS or a local-network exception."
            case .timedOut: return "The source request timed out."
            case .cannotFindHost, .dnsLookupFailed: return "The server address could not be resolved."
            case .cannotConnectToHost: return "A connection to the server could not be established."
            case .notConnectedToInternet: return "The network is unavailable. Check the connection and local-network access."
            case .secureConnectionFailed, .serverCertificateUntrusted, .serverCertificateHasBadDate,
                 .serverCertificateHasUnknownRoot, .serverCertificateNotYetValid:
                return "The server's HTTPS connection or certificate could not be verified."
            default: return "The network request failed (\(error.errorCode))."
            }
        case APIError.http(let status, _): return "The source request returned HTTP \(status)."
        default: return "The source request failed."
        }
    }
}
