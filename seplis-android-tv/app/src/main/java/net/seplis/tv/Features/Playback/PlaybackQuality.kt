package net.seplis.tv.features.playback

import java.text.DecimalFormat

object PlaybackQuality {
    const val maximum = 200_000_000
    val options = listOf(maximum, 80_000_000, 40_000_000, 20_000_000, 12_000_000,
        8_000_000, 6_000_000, 4_000_000, 3_000_000, 1_500_000, 720_000, 420_000)

    fun available(sourceBitrate: Double?, selected: Int) = options.filter {
        it == maximum || it == selected || sourceBitrate != null && it < sourceBitrate
    }

    fun label(bitrate: Int, sourceBitrate: Double? = null): String =
        if (bitrate == maximum) "Max" + (sourceBitrate?.takeIf { it.isFinite() && it > 0 }
            ?.let { " (${format(it)})" } ?: "") else format(bitrate.toDouble())

    private fun format(bitrate: Double): String = if (bitrate < 1_000_000) "${(bitrate / 1000).toInt()} kbps"
        else "${DecimalFormat("0.#").format(bitrate / 1_000_000)} Mbps"
}
