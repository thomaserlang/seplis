package net.seplis.tv.features.library

import org.json.JSONObject
import net.seplis.tv.core.networking.text

data class MediaSummary(val id: Int, val title: String, val poster: Poster?) {
    companion object {
        fun from(json: JSONObject) = MediaSummary(json.getInt("id"), json.text("title") ?: "Untitled", json.poster())
    }
}
