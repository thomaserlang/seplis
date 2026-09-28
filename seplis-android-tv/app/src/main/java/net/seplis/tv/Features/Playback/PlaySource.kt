package net.seplis.tv.features.playback

import net.seplis.tv.core.networking.arrayOrEmpty
import net.seplis.tv.core.networking.flag
import net.seplis.tv.core.networking.integer
import net.seplis.tv.core.networking.number
import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.objects
import net.seplis.tv.core.networking.text
import org.json.JSONObject

data class PlayRequest(val playId: String, val url: String) {
    companion object { fun from(json: JSONObject) = PlayRequest(json.getString("play_id"), json.getString("play_url")) }
}

data class PlayStream(val title: String, val language: String, val groupIndex: Int?,
    val codec: String?, val channels: Int?, val forced: Boolean) {
    val key: String get() = "$language:${groupIndex ?: "null"}"
    companion object { fun from(json: JSONObject) = PlayStream(
        json.text("title")?.takeIf { it.isNotEmpty() } ?: json.text("language") ?: "Unknown", json.text("language") ?: "und",
        json.integer("group_index"), json.text("codec"), json.integer("channels"), json.flag("forced") == true)
    }
}

data class PlaySource(val index: Int, val bitrate: Double, val resolution: String, val codec: String,
    val width: Int, val height: Int, val duration: Double, val audio: List<PlayStream>,
    val subtitles: List<PlayStream>, val hdr: String?, val hdrType: String?, val format: String?,
    val mediaType: String?, val fps: Double? = null, val size: Long? = null) {
    companion object { fun from(json: JSONObject) = PlaySource(
        json.getInt("index"), json.number("bitrate") ?: 0.0, json.text("resolution") ?: "Unknown",
        json.text("codec") ?: "Unknown", json.optInt("width"), json.optInt("height"),
        json.number("duration") ?: 0.0, json.arrayOrEmpty("audio").objects().map(PlayStream::from),
        json.arrayOrEmpty("subtitles").objects().map(PlayStream::from),
        json.text("video_color_range"), json.text("video_color_range_type"), json.text("format"),
        json.text("media_type"), json.number("fps"),
        if (json.isNull("size")) null else json.optLong("size")) }
}

data class PlayCandidate(val request: PlayRequest, val source: PlaySource) {
    val label: String get() = buildList {
        add(source.resolution)
        add(source.codec.uppercase())
        if (source.hdr.equals("hdr", ignoreCase = true)) add(if (source.hdrType.equals("dovi", ignoreCase = true)) "Dolby Vision" else "HDR")
        if (source.bitrate > 0) add("${java.text.DecimalFormat("0.#").format(source.bitrate / 1_000_000)} Mbps")
        java.net.URI(request.url).host?.let { add(it) }
    }.joinToString(" · ")
}
