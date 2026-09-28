package net.seplis.tv.features.home

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CancellationException

class HomeShelfModel(private val repository: HomeRepository, private val shelf: HomeShelf) {
    var items by mutableStateOf<List<HomeItem>>(emptyList())
        private set
    var cursor: String? by mutableStateOf(null)
        private set
    var loading by mutableStateOf(false)
        private set
    var isLoadingMore by mutableStateOf(false)
        private set
    var loaded by mutableStateOf(false)
        private set
    var error: String? by mutableStateOf(null)
        private set
    private var generation = 0

    suspend fun load(more: Boolean = false) {
        if (more && (loading || cursor == null)) return
        val request = ++generation
        loading = true
        isLoadingMore = more
        error = null
        try {
            val (fetched, next) = repository.load(shelf, if (more) cursor else null)
            if (request != generation) return
            val previous = if (more) items else emptyList()
            items = (previous + fetched).distinctBy(HomeItem::key)
            cursor = next
            loaded = true
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) {
            if (request == generation) error = failure.message ?: "Could not load ${shelf.title.lowercase()}"
        } finally {
            if (request == generation) {
                loading = false
                isLoadingMore = false
            }
        }
    }
}
