package net.seplis.tv.features.series

import androidx.compose.runtime.*
import kotlinx.coroutines.CancellationException
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.*

class EpisodesModel(private val reference: MediaReference, private val season: Int?, api: ApiClient) {
    private val repository = SeriesRepository(api)
    private val shared = MediaDetailRepository(api)
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
            episodes = repository.episodes(reference, season)
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not load episodes" }
        finally { loading = false }
    }

    suspend fun changeWatched(episode: Episode, increment: Boolean) {
        if (isUpdating) return
        isUpdating = true
        try {
            shared.update(reference, "episodes/${episode.number}/watched", if (increment) "POST" else "DELETE")
            load()
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { updateError = failure.message ?: "Could not update episode" }
        finally { isUpdating = false }
    }
}
