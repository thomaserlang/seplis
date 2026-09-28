package net.seplis.tv.features.movie

import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.MediaSummary
import net.seplis.tv.core.networking.page

class MovieRepository(private val api: ApiClient) {
    suspend fun movie(ref: MediaReference): Movie = Movie.from(api.objectAt(ref.path,
        mapOf("expand" to "user_watchlist,user_favorite,user_watched")))

    suspend fun canPlay(ref: MediaReference): Boolean = api.arrayAt("${ref.path}/play-servers").length() > 0

    suspend fun collection(collection: MovieCollection, cursor: String? = null) = api.objectAt("movies", mapOf(
        "collection_id" to collection.id.toString(), "sort" to "release_date_asc", "per_page" to "24",
    ) + (cursor?.let { mapOf("cursor" to it) } ?: emptyMap())).page(MediaSummary::from)
}
