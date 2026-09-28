package net.seplis.tv.features.cast

import androidx.compose.runtime.*
import kotlinx.coroutines.CancellationException
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.core.networking.page
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.movie.MovieCastCredit
import net.seplis.tv.features.series.SeriesCastCredit

class CastRowModel(private val reference: MediaReference, private val api: APIClient) {
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
            val query = buildMap {
                put("per_page", "25")
                if (more) cursor?.let { put("cursor", it) }
            }
            val page = api.objectAt("${reference.path}/cast", query).page {
                when (reference.kind) {
                    MediaKind.MOVIE -> MovieCastCredit.from(it).member
                    MediaKind.SERIES -> SeriesCastCredit.from(it).member
                }
            }
            members = ((if (more) members else emptyList()) + page.records).distinctBy { it.id }
            cursor = page.cursor
            hasLoaded = true
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not load cast" }
        finally { isLoading = false }
    }
}
