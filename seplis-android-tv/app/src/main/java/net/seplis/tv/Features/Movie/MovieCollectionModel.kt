package net.seplis.tv.features.movie

import androidx.compose.runtime.*
import kotlinx.coroutines.CancellationException
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.MediaSummary

class MovieCollectionModel(private val collection: MovieCollection, api: ApiClient) {
    private val repository = MovieRepository(api)
    var movies by mutableStateOf<List<MediaSummary>>(emptyList())
        private set
    var cursor by mutableStateOf<String?>(null)
        private set
    var isLoading by mutableStateOf(false)
        private set
    var error by mutableStateOf<String?>(null)
        private set

    suspend fun load(more: Boolean = false) {
        if (isLoading || more && cursor == null) return
        isLoading = true
        error = null
        try {
            val page = repository.collection(collection, if (more) cursor else null)
            movies = ((if (more) movies else emptyList()) + page.records).distinctBy { it.id }
            cursor = page.cursor
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not load collection" }
        finally { isLoading = false }
    }
}
