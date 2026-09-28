package net.seplis.tv.features.series

import org.json.JSONObject
import net.seplis.tv.core.networking.flag
import net.seplis.tv.core.networking.integer
import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.text

import net.seplis.tv.features.library.Watched

data class Episode(
    val number: Int, val season: Int?, val episode: Int?, val title: String?, val plot: String?,
    val airDate: String?, val runtime: Int?, val watched: Watched, val canPlay: Boolean,
) {
    val numberLabel: String get() = if (season != null && episode != null) "S$season E$episode" else "Episode $number"
    val label: String get() = title?.let { "$numberLabel - $it" } ?: numberLabel
    val watchHeading: String get() = if (watched.position > 0) "Continue watching" else "Next to watch"

    companion object {
        fun from(json: JSONObject) = Episode(
            number = json.getInt("number"), season = json.integer("season"), episode = json.integer("episode"),
            title = json.text("title"),
            plot = json.text("plot"), airDate = json.text("air_date"), runtime = json.integer("runtime"),
            watched = Watched.from(json.objectOrNull("user_watched")),
            canPlay = json.objectOrNull("user_can_watch")?.flag("on_play_server") != false,
        )
    }
}

data class Season(val number: Int, val total: Int) {
    companion object { fun from(json: JSONObject) = Season(json.getInt("season"), json.optInt("total")) }
}
