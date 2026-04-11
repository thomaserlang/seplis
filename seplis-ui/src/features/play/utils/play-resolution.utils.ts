const bitrateResolutionThresholds: Record<string, [number, number][]> = {
    h264: [
        [1_000_000, 480],
        [2_000_000, 720],
        [5_000_000, 1080],
        [12_000_000, 1440],
        [Infinity, 2160],
    ],
    h265: [
        [500_000, 480],
        [1_000_000, 720],
        [3_000_000, 1080],
        [8_000_000, 1440],
        [Infinity, 2160],
    ],
    hevc: [
        [500_000, 480],
        [1_000_000, 720],
        [3_000_000, 1080],
        [8_000_000, 1440],
        [Infinity, 2160],
    ],
    av1: [
        [300_000, 480],
        [800_000, 720],
        [2_000_000, 1080],
        [6_000_000, 1440],
        [Infinity, 2160],
    ],
}

export function recommendResolution(bitrate: number, codec: string): number {
    if (!(codec in bitrateResolutionThresholds)) {
        return 2160
    }

    for (const [maxBr, res] of bitrateResolutionThresholds[codec]) {
        if (bitrate < maxBr) {
            return res
        }
    }

    return 2160
}
