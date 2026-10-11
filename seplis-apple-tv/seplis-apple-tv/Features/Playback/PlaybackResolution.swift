import Foundation

enum PlaybackResolution {
    // Same thresholds and strict comparisons as seplis-ui's play-resolution.utils.ts.
    private static let thresholds: [String: [(Int, Int)]] = [
        "h264": [(1_000_000, 854), (2_000_000, 1280), (5_000_000, 1920), (12_000_000, 2560)],
        "hevc": [(500_000, 854), (1_000_000, 1280), (3_000_000, 1920), (8_000_000, 2560)],
        "av1": [(300_000, 854), (800_000, 1280), (2_000_000, 1920), (6_000_000, 2560)],
    ]

    static func recommendWidth(bitrate: Int, codec: String) -> Int {
        thresholds[codec == "h265" ? "hevc" : codec]?.first { bitrate < $0.0 }?.1 ?? 3840
    }
}
