package net.seplis.tv.features.series

import net.seplis.tv.features.library.Poster
import net.seplis.tv.features.library.MediaDetailInfo
import net.seplis.tv.features.series.Season
import net.seplis.tv.core.networking.arrayOrEmpty
import net.seplis.tv.core.networking.flag
import net.seplis.tv.core.networking.integer
import net.seplis.tv.core.networking.number
import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.objects
import net.seplis.tv.features.library.poster
import net.seplis.tv.core.networking.text
import org.json.JSONObject

data class Series(
    val id: Int, override val title: String, override val originalTitle: String?, override val tagline: String?, override val plot: String?,
    val poster: Poster?, override val genres: List<String>, val year: String?, val endedYear: String?, val runtime: Int?,
    val language: String?, val rating: Double?, val status: Int?, val totalEpisodes: Int?,
    val seasons: List<Season>, val watchlist: Boolean, val favorite: Boolean,
) : MediaDetailInfo {
    override val detailFacts get() = detailFacts()

    companion object {
        fun from(json: JSONObject) = Series(
            id = json.getInt("id"), title = json.text("title") ?: json.text("original_title") ?: "Untitled",
            originalTitle = json.text("original_title"), tagline = json.text("tagline"), plot = json.text("plot"),
            poster = json.poster(), genres = json.arrayOrEmpty("genres").objects().mapNotNull { it.text("name") },
            year = json.text("premiered")?.take(4), endedYear = json.text("ended")?.take(4),
            runtime = json.integer("runtime"),
            language = json.text("language"), rating = json.number("rating"), status = json.integer("status"),
            totalEpisodes = json.integer("total_episodes"),
            seasons = json.arrayOrEmpty("seasons").objects().map(Season::from),
            watchlist = json.objectOrNull("user_watchlist")?.flag("on_watchlist") == true,
            favorite = json.objectOrNull("user_favorite")?.flag("favorite") == true,
        )
    }
}
