package net.seplis.tv.features.movie

import androidx.compose.runtime.*
import kotlinx.coroutines.CancellationException
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.core.networking.page
import net.seplis.tv.features.library.MediaSummary

class MovieCollectionModel(private val collection: MovieCollection, private val api: APIClient) {
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
            val query = buildMap {
                put("collection_id", collection.id.toString())
                put("sort", "release_date_asc")
                put("per_page", "24")
                if (more) cursor?.let { put("cursor", it) }
            }
            val page = api.objectAt("movies", query).page(MediaSummary::from)
            movies = ((if (more) movies else emptyList()) + page.records).distinctBy { it.id }
            cursor = page.cursor
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not load collection" }
        finally { isLoading = false }
    }
}
