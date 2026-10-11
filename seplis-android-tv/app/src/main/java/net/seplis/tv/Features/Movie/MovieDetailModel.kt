package net.seplis.tv.features.movie

import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.topshelf.WatchHistory

class MovieDetailModel(val reference: MediaReference, private val api: APIClient) {
    var isUpdating by mutableStateOf(false)
        private set
    var movie by mutableStateOf<Movie?>(null)
    var canPlay by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
    private var isLoading = false

    suspend fun load() {
        if (isLoading) return
        isLoading = true
        error = null
        try {
            val loaded = Movie.from(api.objectAt(reference.path,
                mapOf("expand" to "user_watchlist,user_favorite,user_watched")))
            canPlay = api.arrayAt("${reference.path}/play-servers").length() > 0
            movie = loaded
            error = null
        } catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message }
        finally { isLoading = false }
    }
    suspend fun toggleWatchlist() = update("watchlist", if (movie?.watchlist == true) "DELETE" else "PUT")
    suspend fun toggleFavorite() = update("favorite", if (movie?.favorite == true) "DELETE" else "PUT")
    suspend fun changeWatched(increment: Boolean) = update("watched", if (increment) "POST" else "DELETE")

    private suspend fun update(path: String, method: String) {
        if (isUpdating) return
        isUpdating = true
        try {
            api.perform("${reference.path}/$path", method)
            if (path == "watched") WatchHistory.notifyChanged()
            load()
        }
        catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not update movie" }
        finally { isUpdating = false }
    }

}
