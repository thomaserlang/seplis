package net.seplis.tv.features.search
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.core.networking.objects
import net.seplis.tv.core.networking.text
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.Poster
import net.seplis.tv.features.library.poster

data class SearchResult(val reference: MediaReference, val title: String, val poster: Poster?)

class SearchModel(private val api: APIClient) {
    var results by mutableStateOf<List<SearchResult>>(emptyList())
        private set
    var error by mutableStateOf<String?>(null)
        private set
    var isLoading by mutableStateOf(false)
        private set
    private var generation = 0

    suspend fun search(text: String) {
        val term = text.trim()
        val current = ++generation
        results = emptyList()
        error = null
        isLoading = term.isNotBlank()
        if (term.isBlank()) return
        try {
            delay(300)
            val found = api.arrayAt("search", mapOf("query" to term, "limit" to "60")).objects().map {
                SearchResult(MediaReference(MediaKind.from(it.text("type")), it.getInt("id")),
                    it.text("title") ?: "Untitled", it.poster())
            }
            if (current == generation) {
                results = found
                error = null
            }
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { if (current == generation) error = failure.message }
        finally { if (current == generation) isLoading = false }
    }
}
