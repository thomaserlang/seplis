package net.seplis.tv.features.series

import androidx.compose.runtime.*
import kotlinx.coroutines.CancellationException
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.core.networking.page
import net.seplis.tv.features.topshelf.WatchHistory
import net.seplis.tv.features.library.*

class EpisodesModel(private val reference: MediaReference, private val season: Int?, private val api: APIClient) {
    var episodes by mutableStateOf<List<Episode>?>(null)
        private set
    var error by mutableStateOf<String?>(null)
        private set
    var updateError by mutableStateOf<String?>(null)
    var isUpdating by mutableStateOf(false)
        private set
    private var loading = false

    suspend fun load() {
        if (loading) return
        loading = true
        error = null
        try {
            val result = mutableListOf<Episode>()
            var cursor: String? = null
            do {
                val query = buildMap {
                    put("expand", "user_watched,user_can_watch")
                    put("per_page", "100")
                    season?.let { put("season", it.toString()) }
                    cursor?.let { put("cursor", it) }
                }
                val page = api.objectAt("${reference.path}/episodes", query).page(Episode::from)
                result += page.records
                cursor = page.cursor
            } while (cursor != null)
            episodes = result
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not load episodes" }
        finally { loading = false }
    }

    suspend fun changeWatched(episode: Episode, increment: Boolean) {
        if (isUpdating) return
        isUpdating = true
        try {
            api.perform("${reference.path}/episodes/${episode.number}/watched", if (increment) "POST" else "DELETE")
            WatchHistory.notifyChanged()
            load()
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { updateError = failure.message ?: "Could not update episode" }
        finally { isUpdating = false }
    }
}
