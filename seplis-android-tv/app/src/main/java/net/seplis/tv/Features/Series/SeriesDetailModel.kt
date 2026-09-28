package net.seplis.tv.features.series

import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.series.Episode
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.cast.CastMember
import net.seplis.tv.features.cast.CastRepository
import net.seplis.tv.features.library.MediaDetailRepository
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope

class SeriesDetailModel(private val ref: MediaReference, api: ApiClient) {
    var isUpdating by mutableStateOf(false)
        private set
    val repository = SeriesRepository(api)
    val shared = MediaDetailRepository(api)
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
            val loaded = repository.series(ref)
            val (nextEpisode, lastEpisode) = coroutineScope {
                val next = async { repository.episodeToWatch(ref) }
                val last = async { repository.lastWatched(ref) }
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
        try { shared.update(ref, path, method); load() }
        catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not update series" }
        finally { isUpdating = false }
    }

}
