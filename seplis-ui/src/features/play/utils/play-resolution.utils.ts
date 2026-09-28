// Widths for the 480p, 720p, 1080p, 1440p, and 2160p tiers, sent as max_width.
const bitrateWidthThresholds: Record<string, [number, number][]> = {
    h264: [
        [1_000_000, 854],
        [2_000_000, 1280],
        [5_000_000, 1920],
        [12_000_000, 2560],
        [Infinity, 3840],
    ],
    h265: [
        [500_000, 854],
        [1_000_000, 1280],
        [3_000_000, 1920],
        [8_000_000, 2560],
        [Infinity, 3840],
    ],
    hevc: [
        [500_000, 854],
        [1_000_000, 1280],
        [3_000_000, 1920],
        [8_000_000, 2560],
        [Infinity, 3840],
    ],
    av1: [
        [300_000, 854],
        [800_000, 1280],
        [2_000_000, 1920],
        [6_000_000, 2560],
        [Infinity, 3840],
    ],
}

export function recommendWidth(bitrate: number, codec: string): number {
    if (!(codec in bitrateWidthThresholds)) {
        return 3840
    }

    for (const [maxBr, width] of bitrateWidthThresholds[codec]) {
        if (bitrate < maxBr) {
            return width
        }
    }

    return 3840
}
