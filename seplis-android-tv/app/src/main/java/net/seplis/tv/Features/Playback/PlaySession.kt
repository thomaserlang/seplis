package net.seplis.tv.features.playback

import net.seplis.tv.core.networking.objectOrNull
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import org.json.JSONObject

data class PlaySession(val hlsUrl: String, val keepAliveUrl: String, val closeUrl: String,
    val decision: TranscodeDecision?)

fun JSONObject.playSession(base: String): PlaySession = PlaySession(
    resolvePlayUrl(base, getString("hls_url")),
    resolvePlayUrl(base, getString("keep_alive_url")),
    resolvePlayUrl(base, getString("close_session_url")), objectOrNull("transcode_decision")?.let(TranscodeDecision::from))

internal fun resolvePlayUrl(base: String, value: String): String {
    // Leading-slash paths belong to the server's mount point, as on Apple TV.
    val url = if (value.startsWith('/')) (base.trimEnd('/') + value).toHttpUrlOrNull()
        else (base.trimEnd('/') + "/").toHttpUrlOrNull()?.resolve(value)
    return requireNotNull(url) { "Invalid play-server URL" }.toString()
}
