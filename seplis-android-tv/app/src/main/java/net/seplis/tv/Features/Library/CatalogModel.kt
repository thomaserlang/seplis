package net.seplis.tv.features.library
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CancellationException
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaSummary

class CatalogModel(private val kind: MediaKind, api: ApiClient) {
    private val repository = CatalogRepository(api)
    private var lastLoaded: Pair<CatalogFilters, Int>? = null
    var items by mutableStateOf<List<MediaSummary>>(emptyList())
        private set
    var filters by mutableStateOf(CatalogFilters())
    var cursor: String? by mutableStateOf(null)
        private set
    var loading by mutableStateOf(false)
        private set
    var hasLoaded by mutableStateOf(false)
        private set
    var error: String? by mutableStateOf(null)
        private set
    private var requestVersion = 0
    var focusedID: Int? by mutableStateOf(null)
    var restoreFocusPending = false

    suspend fun genres(): List<Pair<Int, String>> = repository.genres(kind)

    suspend fun ensureLoaded(refresh: Int) {
        val key = filters to refresh
        if (lastLoaded == key) return
        load()
        if (error == null) lastLoaded = key
    }

    suspend fun load(more: Boolean = false) {
        if (more && (loading || cursor == null)) return
        val version = ++requestVersion
        val currentFilters = filters
        val currentCursor = if (more) cursor else null
        loading = true
        error = null
        if (!more) { items = emptyList(); cursor = null }
        try {
            val page = repository.catalog(kind, currentFilters, currentCursor)
            if (version != requestVersion) return
            val previous = if (more) items else emptyList()
            items = (previous + page.records).distinctBy(MediaSummary::id)
            if (!more && items.none { it.id == focusedID }) focusedID = null
            cursor = page.cursor
            hasLoaded = true
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { if (version == requestVersion) error = failure.message }
        finally { if (version == requestVersion) loading = false }
    }
}
