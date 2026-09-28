package net.seplis.tv.features.library

import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.MediaSummary
import net.seplis.tv.core.networking.page

class CatalogRepository(private val api: ApiClient) {
    suspend fun catalog(kind: MediaKind, filters: CatalogFilters, cursor: String? = null) =
        api.objectAt(kind.path, filters.query(kind, cursor)).page(MediaSummary::from)

    suspend fun genres(kind: MediaKind): List<Pair<Int, String>> =
        api.arrayAt("genres", mapOf("type" to kind.name.lowercase())).let { data ->
            (0 until data.length()).map { data.getJSONObject(it) }
                .map { it.getInt("id") to it.getString("name") }
        }
}
