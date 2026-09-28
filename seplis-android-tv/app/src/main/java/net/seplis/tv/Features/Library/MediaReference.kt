package net.seplis.tv.features.library

import org.json.JSONObject
import net.seplis.tv.core.networking.flag
import net.seplis.tv.core.networking.integer
import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.text

enum class MediaKind(val path: String) { MOVIE("movies"), SERIES("series");
    companion object { fun from(value: String?) = if (value == "movie") MOVIE else SERIES }
}

data class MediaReference(val kind: MediaKind, val id: Int) {
    val path: String get() = "${kind.path}/$id"
}
