package net.seplis.tv.features.home

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CancellationException
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.page
import net.seplis.tv.core.networking.text
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.MediaSummary
import net.seplis.tv.features.series.Episode

class HomeShelfModel(private val api: APIClient, val shelf: HomeShelf) {
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
            val (fetched, next) = loadPage(if (more) cursor else null)
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

    private suspend fun loadPage(cursor: String?): Pair<List<HomeItem>, String?> {
        val page = api.objectAt(shelf.path, shelf.query(cursor))
        return when (shelf) {
            HomeShelf.WATCHED -> {
                val records = page.page { json ->
                    val media = MediaSummary.from(json.getJSONObject("data"))
                    HomeItem(MediaReference(MediaKind.from(json.text("type")), media.id), media)
                }
                records.records to records.cursor
            }
            HomeShelf.TO_WATCH, HomeShelf.RECENTLY_AIRED -> {
                val records = page.page { json ->
                    val media = MediaSummary.from(json.getJSONObject("series"))
                    HomeItem(MediaReference(MediaKind.SERIES, media.id), media,
                        json.objectOrNull("episode")?.let(Episode::from))
                }
                records.records to records.cursor
            }
            else -> {
                val records = page.page(MediaSummary::from)
                records.records.map { HomeItem(MediaReference(shelf.kind, it.id), it) } to records.cursor
            }
        }
    }
}
