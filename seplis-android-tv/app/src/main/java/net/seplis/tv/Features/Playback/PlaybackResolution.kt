package net.seplis.tv.features.playback

object PlaybackResolution {
    // Same thresholds and strict comparisons as seplis-ui's play-resolution.utils.ts.
    private val thresholds = mapOf(
        "h264" to listOf(1_000_000 to 854, 2_000_000 to 1280, 5_000_000 to 1920, 12_000_000 to 2560),
        "hevc" to listOf(500_000 to 854, 1_000_000 to 1280, 3_000_000 to 1920, 8_000_000 to 2560),
        "av1" to listOf(300_000 to 854, 800_000 to 1280, 2_000_000 to 1920, 6_000_000 to 2560),
    )

    fun recommendWidth(bitrate: Int, codec: String): Int =
        thresholds[if (codec == "h265") "hevc" else codec]?.firstOrNull { bitrate < it.first }?.second ?: 3840
}
