package net.seplis.tv.features.playback

import androidx.compose.foundation.border
import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import net.seplis.tv.components.LibraryStyle
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

@Composable
internal fun PlaybackInfoRow(label: String, value: String, modifier: Modifier = Modifier) {
    var focused by remember { mutableStateOf(false) }
    Column(modifier.fillMaxWidth().border(1.5.dp, if (focused) Color.White else Color.Transparent, RoundedCornerShape(4.dp))
        .onFocusChanged { focused = it.isFocused }.focusable().padding(12.dp)) {
        Text(label, color = LibraryStyle.muted, fontSize = 11.sp, lineHeight = 14.sp)
        Text(value, fontSize = 13.sp, lineHeight = 17.sp)
    }
}
