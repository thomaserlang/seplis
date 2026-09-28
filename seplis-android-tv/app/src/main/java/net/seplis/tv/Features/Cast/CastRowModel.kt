package net.seplis.tv.features.cast

import androidx.compose.runtime.*
import kotlinx.coroutines.CancellationException
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.MediaReference

class CastRowModel(private val reference: MediaReference, api: ApiClient) {
    private val repository = CastRepository(api)
    var hasLoaded by mutableStateOf(false)
        private set
    var members by mutableStateOf<List<CastMember>>(emptyList())
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
            val page = repository.cast(reference, if (more) cursor else null)
            members = ((if (more) members else emptyList()) + page.records).distinctBy { it.id }
            cursor = page.cursor
            hasLoaded = true
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not load cast" }
        finally { isLoading = false }
    }
}
