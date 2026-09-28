package net.seplis.tv.features.home

import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.series.Episode
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.MediaSummary
import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.objects
import net.seplis.tv.core.networking.page
import net.seplis.tv.core.networking.text

enum class HomeShelf(val title: String, val kind: MediaKind, val path: String, val sort: String? = null) {
    WATCHED("Watched", MediaKind.SERIES, "users/me/watched"),
    TO_WATCH("Series to Watch", MediaKind.SERIES, "series/to-watch"),
    MOVIE_WATCHLIST("Movie watchlist", MediaKind.MOVIE, "movies", "user_watchlist_added_at_desc"),
    RECENT_SERIES("Series recently added", MediaKind.SERIES, "series", "user_play_server_series_added_desc"),
    RECENT_MOVIES("Movies recently added", MediaKind.MOVIE, "movies", "user_play_server_movie_added_desc"),
    POPULAR_SERIES("Popular series", MediaKind.SERIES, "series", "popularity_desc"),
    POPULAR_MOVIES("Popular movies", MediaKind.MOVIE, "movies", "popularity_desc"),
    RECENTLY_AIRED("Episodes recently aired", MediaKind.SERIES, "series/recently-aired"),
    SERIES_WATCHLIST("Series watchlist", MediaKind.SERIES, "series", "user_watchlist_added_at_desc"),
    UNWATCHED_SERIES("Series you haven't watched", MediaKind.SERIES, "series"),
    UNWATCHED_MOVIES("Movies you haven't watched", MediaKind.MOVIE, "movies"),
    FAVORITE_SERIES("Series favorites", MediaKind.SERIES, "series", "user_favorite_added_at_desc"),
    FAVORITE_MOVIES("Movie favorites", MediaKind.MOVIE, "movies", "user_favorite_added_at_desc");

    fun query(cursor: String? = null): Map<String, String> = buildMap {
        put("user_can_watch", "true")
        put("per_page", "24")
        sort?.let { put("sort", it) }
        if (this@HomeShelf == RECENTLY_AIRED) put("days_ahead", "7")
        if (this@HomeShelf == MOVIE_WATCHLIST || this@HomeShelf == SERIES_WATCHLIST) put("user_watchlist", "true")
        if (this@HomeShelf == UNWATCHED_SERIES || this@HomeShelf == UNWATCHED_MOVIES) put("user_has_watched", "false")
        if (this@HomeShelf == FAVORITE_SERIES || this@HomeShelf == FAVORITE_MOVIES) put("user_favorites", "true")
        cursor?.let { put("cursor", it) }
    }
}

data class HomeItem(val reference: MediaReference, val media: MediaSummary, val episode: Episode? = null) {
    val key: String get() = "${reference.kind}-${reference.id}-${episode?.number ?: 0}"
}

class HomeRepository(private val api: ApiClient) {
    suspend fun load(shelf: HomeShelf, cursor: String? = null): Pair<List<HomeItem>, String?> {
        val page = api.objectAt(shelf.path, shelf.query(cursor))
        return when (shelf) {
            HomeShelf.WATCHED -> {
                val records = page.page { json ->
                    val media = MediaSummary.from(json.getJSONObject("data"))
                    HomeItem(MediaReference(MediaKind.from(json.text("type")), media.id), media)
                }
                records.records to records.cursor
            }
            HomeShelf.TO_WATCH, HomeShelf.RECENTLY_AIRED -> {
                val records = page.page { json ->
                    val media = MediaSummary.from(json.getJSONObject("series"))
                    HomeItem(MediaReference(MediaKind.SERIES, media.id), media,
                        json.objectOrNull("episode")?.let(Episode::from))
                }
                records.records to records.cursor
            }
            else -> {
                val records = page.page(MediaSummary::from)
                records.records.map { HomeItem(MediaReference(shelf.kind, it.id), it) } to records.cursor
            }
        }
    }
}
