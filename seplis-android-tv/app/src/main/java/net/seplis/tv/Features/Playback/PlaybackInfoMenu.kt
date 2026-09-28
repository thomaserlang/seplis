package net.seplis.tv.features.playback

import java.net.URI
import java.text.DecimalFormat

object PlaybackInfoMenu {
    fun method(decision: TranscodeDecision?): String = decision?.playbackMethod ?: "Unavailable"

    fun decision(decision: TranscodeDecision?, server: String?): List<Pair<String, String>> = buildList {
        add("Delivery" to "HLS stream")
        if (decision == null) add("Transcoding" to "Not reported by the play server")
        else {
            add("Video" to decision.video.label)
            add("Audio" to decision.audio.label)
            decision.reasons.forEach { add("Reason" to it) }
        }
        server?.let { add("Server" to (runCatching { URI(it).host }.getOrNull() ?: it)) }
    }

    fun source(source: PlaySource, audioKey: String?): List<Pair<String, String>> = buildList {
        val number = DecimalFormat("0.##")
        add("Quality" to source.resolution)
        add("Video codec" to source.codec.uppercase())
        if (source.width > 0 && source.height > 0) add("Dimensions" to "${source.width} x ${source.height}")
        source.format?.let { add("Container" to it.uppercase()) }
        source.hdr?.let { add("Color range" to it.uppercase()) }
        source.hdrType?.takeIf(String::isNotBlank)?.let { add("HDR format" to it.uppercase()) }
        source.fps?.takeIf { it > 0 }?.let { add("Frame rate" to "${DecimalFormat("0.###").format(it)} fps") }
        if (source.bitrate > 0) add("Bitrate" to "${number.format(source.bitrate / 1_000_000)} Mbps")
        source.size?.takeIf { it > 0 }?.let { add("File size" to "${number.format(it / 1_000_000_000.0)} GB") }
        source.audio.firstOrNull { it.key == audioKey }?.let { audio ->
            audio.codec?.let { add("Audio codec" to it.uppercase()) }
            audio.channels?.let { add("Audio channels" to it.toString()) }
            add("Audio language" to audio.language)
        }
    }
}
