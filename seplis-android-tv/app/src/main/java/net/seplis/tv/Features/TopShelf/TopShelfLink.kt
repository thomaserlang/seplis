package net.seplis.tv.features.topshelf

import android.net.Uri
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference

data class TopShelfLink(val accountID: Int, val reference: MediaReference, val episodeNumber: Int?, val play: Boolean) {
    val uri: Uri get() = Uri.Builder().scheme("seplis").authority("top-shelf")
        .appendPath(if (reference.kind == MediaKind.MOVIE) "movie" else "series")
        .appendPath(reference.id.toString()).appendQueryParameter("account", accountID.toString())
        .appendQueryParameter("action", if (play) "play" else "details")
        .apply { episodeNumber?.let { appendQueryParameter("episode", it.toString()) } }.build()

    companion object {
        fun parse(uri: Uri?): TopShelfLink? {
            if (uri == null || uri.scheme != "seplis" || uri.host != "top-shelf") return null
            val path = uri.pathSegments
            if (path.size != 2 || path[0] !in listOf("movie", "series")) return null
            val id = path[1].toIntOrNull()?.takeIf { it > 0 } ?: return null
            val account = uri.getQueryParameter("account")?.toIntOrNull()?.takeIf { it > 0 } ?: return null
            val action = uri.getQueryParameter("action")?.takeIf { it in listOf("play", "details") } ?: return null
            val rawEpisode = uri.getQueryParameter("episode")
            val episode = rawEpisode?.toIntOrNull()?.takeIf { it > 0 }
            if (rawEpisode != null && episode == null || path[0] == "series" && action == "play" && episode == null) return null
            return TopShelfLink(account, MediaReference(MediaKind.from(path[0]), id), episode, action == "play")
        }
    }
}
