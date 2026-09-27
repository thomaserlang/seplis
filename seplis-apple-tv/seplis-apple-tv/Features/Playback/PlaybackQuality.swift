import Foundation

enum PlaybackQuality {
    static let maximum = 200_000_000
    static let defaultBitrate = maximum
    static let options = [maximum, 80_000_000, 40_000_000, 20_000_000, 12_000_000,
                          8_000_000, 6_000_000, 4_000_000, 3_000_000, 1_500_000, 720_000, 420_000]

    static func label(_ bitrate: Int, sourceBitrate: Double? = nil) -> String {
        if bitrate == maximum {
            guard let sourceBitrate, sourceBitrate.isFinite, sourceBitrate > 0 else { return "Max" }
            return "Max (\(formattedBitrate(sourceBitrate)))"
        }
        return formattedBitrate(Double(bitrate))
    }

    private static func formattedBitrate(_ bitrate: Double) -> String {
        if bitrate < 1_000_000 { return "\(Int(bitrate / 1000)) kbps" }
        return "\((Double(bitrate) / 1_000_000).formatted(.number.precision(.fractionLength(0...1)))) Mbps"
    }
}
