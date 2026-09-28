package net.seplis.tv.features.movie

import net.seplis.tv.features.library.Poster
import net.seplis.tv.features.library.MediaDetailInfo
import net.seplis.tv.features.library.Watched
import net.seplis.tv.core.networking.arrayOrEmpty
import net.seplis.tv.core.networking.flag
import net.seplis.tv.core.networking.integer
import net.seplis.tv.core.networking.number
import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.objects
import net.seplis.tv.features.library.poster
import net.seplis.tv.core.networking.text
import org.json.JSONObject

data class Movie(
    val id: Int, override val title: String, override val originalTitle: String?, override val tagline: String?, override val plot: String?,
    val poster: Poster?, override val genres: List<String>, val year: String?, val runtime: Int?,
    val language: String?, val rating: Double?, val status: Int?, val budget: Long?, val revenue: Long?,
    val watched: Watched, val watchlist: Boolean, val favorite: Boolean,
    val collection: MovieCollection?,
) : MediaDetailInfo {
    override val detailFacts get() = detailFacts()

    companion object {
        fun from(json: JSONObject) = Movie(
            id = json.getInt("id"), title = json.text("title") ?: json.text("original_title") ?: "Untitled",
            originalTitle = json.text("original_title"), tagline = json.text("tagline"), plot = json.text("plot"),
            poster = json.poster(), genres = json.arrayOrEmpty("genres").objects().mapNotNull { it.text("name") },
            year = json.text("release_date")?.take(4), runtime = json.integer("runtime"),
            language = json.text("language"), rating = json.number("rating"), status = json.integer("status"),
            budget = if (json.isNull("budget")) null else json.getLong("budget"),
            revenue = if (json.isNull("revenue")) null else json.getLong("revenue"),
            watched = Watched.from(json.objectOrNull("user_watched")),
            watchlist = json.objectOrNull("user_watchlist")?.flag("on_watchlist") == true,
            favorite = json.objectOrNull("user_favorite")?.flag("favorite") == true,
            collection = json.objectOrNull("collection")?.let(MovieCollection::from),
        )
    }
}

data class MovieCollection(val id: Int, val name: String) {
    companion object { fun from(json: JSONObject) = MovieCollection(json.getInt("id"), json.text("name") ?: "Collection") }
}
