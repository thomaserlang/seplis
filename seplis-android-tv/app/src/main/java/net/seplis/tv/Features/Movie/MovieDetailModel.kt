package net.seplis.tv.features.movie

import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.MediaSummary
import net.seplis.tv.features.cast.CastMember
import net.seplis.tv.features.cast.CastRepository
import net.seplis.tv.features.library.MediaDetailRepository

class MovieDetailModel(private val ref: MediaReference, api: ApiClient) {
    var isUpdating by mutableStateOf(false)
        private set
    val repository = MovieRepository(api)
    val shared = MediaDetailRepository(api)
    var movie by mutableStateOf<Movie?>(null)
    var canPlay by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
    private var isLoading = false

    suspend fun load() {
        if (isLoading) return
        isLoading = true
        error = null
        try {
            val loaded = repository.movie(ref)
            canPlay = repository.canPlay(ref)
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
        try { shared.update(ref, path, method); load() }
        catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not update movie" }
        finally { isUpdating = false }
    }

}
