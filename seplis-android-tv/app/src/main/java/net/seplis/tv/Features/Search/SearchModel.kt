package net.seplis.tv.features.search
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CancellationException
import net.seplis.tv.core.networking.ApiClient

class SearchModel(api: ApiClient) {
    private val repository = SearchRepository(api)
    var loadedQuery: String? = null
        private set
    var query by mutableStateOf("")
    var results by mutableStateOf<List<SearchResult>>(emptyList())
        private set
    var error by mutableStateOf<String?>(null)
        private set
    var isLoading by mutableStateOf(false)
        private set
    var focusedKey: String? by mutableStateOf(null)
    var restoreFocusPending = false
    private var generation = 0
    private var displayedQuery = ""

    fun prepareQuery() {
        if (displayedQuery == query.trim()) return
        displayedQuery = query.trim()
        loadedQuery = null
        generation++
        results = emptyList()
        error = null
        isLoading = query.isNotBlank()
        focusedKey = null
    }

    suspend fun load() {
        val term = query.trim()
        if (term.isBlank()) return
        val current = ++generation
        isLoading = true
        error = null
        try {
            val found = repository.search(term)
            if (current == generation && term == query.trim()) {
                results = found
                error = null
                loadedQuery = query
            }
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { if (current == generation) error = failure.message }
        finally { if (current == generation) isLoading = false }
    }
}
