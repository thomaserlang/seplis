package net.seplis.tv.features.series

import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.features.series.Episode
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.topshelf.WatchHistory
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

class SeriesDetailModel(val reference: MediaReference, private val api: APIClient) {
    var isUpdating by mutableStateOf(false)
        private set
    var series by mutableStateOf<Series?>(null)
    var next by mutableStateOf<Episode?>(null)
    var last by mutableStateOf<Episode?>(null)
    var error by mutableStateOf<String?>(null)
    private var isLoading = false

    suspend fun load() {
        if (isLoading) return
        isLoading = true
        error = null
        try {
            val loaded = Series.from(api.objectAt(reference.path,
                mapOf("expand" to "user_watchlist,user_favorite")))
            val (nextEpisode, lastEpisode) = coroutineScope {
                val next = async { api.optionalObject("${reference.path}/episode-to-watch")?.let(Episode::from) }
                val last = async { api.optionalObject("${reference.path}/episode-last-watched")?.let(Episode::from) }
                next.await() to last.await()
            }
            next = nextEpisode
            last = lastEpisode
            series = loaded
            error = null
        } catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message }
        finally { isLoading = false }
    }
    suspend fun toggleWatchlist() = update("watchlist", if (series?.watchlist == true) "DELETE" else "PUT")
    suspend fun toggleFavorite() = update("favorite", if (series?.favorite == true) "DELETE" else "PUT")
    suspend fun changeWatched(episode: Episode, increment: Boolean) =
        update("episodes/${episode.number}/watched", if (increment) "POST" else "DELETE")

    private suspend fun update(path: String, method: String) {
        if (isUpdating) return
        isUpdating = true
        try {
            api.perform("${reference.path}/$path", method)
            if (path.endsWith("watched")) WatchHistory.notifyChanged()
            load()
        }
        catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not update series" }
        finally { isUpdating = false }
    }

}
