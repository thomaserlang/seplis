package net.seplis.tv.features.search

import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.core.networking.text
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.Poster
import net.seplis.tv.features.library.poster

data class SearchResult(val reference: MediaReference, val title: String, val poster: Poster?)

class SearchRepository(private val api: ApiClient) {
    suspend fun search(text: String): List<SearchResult> = api.arrayAt("search", mapOf("query" to text))
        .let { results -> (0 until results.length()).map { results.getJSONObject(it) } }
        .map { SearchResult(MediaReference(MediaKind.from(it.text("type")), it.getInt("id")),
            it.text("title") ?: "Untitled", it.poster()) }
}
