package net.seplis.tv.features.library

import org.json.JSONObject
import net.seplis.tv.core.networking.flag
import net.seplis.tv.core.networking.integer
import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.text

data class Poster(val url: String) {
    val thumbnail: String get() = if (url.startsWith("file:")) url else "${url}@SX320.webp"
}

fun JSONObject.poster(): Poster? = objectOrNull("poster_image")?.text("url")?.let(::Poster)

data class MediaSummary(val id: Int, val title: String, val poster: Poster?) {
    companion object {
        fun from(json: JSONObject) = MediaSummary(json.getInt("id"), json.text("title") ?: "Untitled", json.poster())
    }
}
