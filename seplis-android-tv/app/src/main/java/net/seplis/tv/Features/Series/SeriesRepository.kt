package net.seplis.tv.features.series

import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.series.Episode
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.core.networking.page

class SeriesRepository(private val api: ApiClient) {
    suspend fun series(ref: MediaReference): Series = Series.from(api.objectAt(ref.path,
        mapOf("expand" to "user_watchlist,user_favorite")))

    suspend fun episodeToWatch(ref: MediaReference): Episode? =
        api.optionalObject("${ref.path}/episode-to-watch")?.let(Episode::from)

    suspend fun lastWatched(ref: MediaReference): Episode? =
        api.optionalObject("${ref.path}/episode-last-watched")?.let(Episode::from)

    suspend fun episodes(ref: MediaReference, season: Int?): List<Episode> {
        val all = mutableListOf<Episode>()
        var cursor: String? = null
        do {
            val query = buildMap {
                put("expand", "user_watched,user_can_watch")
                put("per_page", "100")
                season?.let { put("season", it.toString()) }
                cursor?.let { put("cursor", it) }
            }
            val page = api.objectAt("${ref.path}/episodes", query).page(Episode::from)
            all += page.records
            cursor = page.cursor
        } while (cursor != null)
        return all
    }
}
