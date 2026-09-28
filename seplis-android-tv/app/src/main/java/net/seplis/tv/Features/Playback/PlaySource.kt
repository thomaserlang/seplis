package net.seplis.tv.features.playback

import org.json.JSONObject

data class PlayRequest(val playId: String, val url: String) {
    companion object { fun from(json: JSONObject) = PlayRequest(json.getString("play_id"), json.getString("play_url")) }
}

data class PlayStream(val title: String, val language: String, val groupIndex: Int?,
    val codec: String?, val channels: Int?, val forced: Boolean) {
    val key: String get() = "$language:${groupIndex ?: "null"}"
    companion object
}

data class PlaySource(val index: Int, val bitrate: Double, val resolution: String, val codec: String,
    val width: Int, val height: Int, val duration: Double, val audio: List<PlayStream>,
    val subtitles: List<PlayStream>, val hdr: String?, val hdrType: String?, val format: String?,
    val mediaType: String?, val fps: Double? = null, val size: Long? = null) {
    companion object
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
