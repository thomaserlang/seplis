package net.seplis.tv

import kotlinx.coroutines.*
import net.seplis.tv.core.networking.*
import net.seplis.tv.features.cast.CastRowModel
import net.seplis.tv.features.library.*
import net.seplis.tv.features.movie.*
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

class LibraryModelTests {
    @Test fun movieIsNotPublishedBeforePlaybackAvailabilityIsKnown() = runBlocking {
        withContext(Dispatchers.Main) {
            val requested = CompletableDeferred<Unit>()
            val release = CompletableDeferred<Unit>()
            val api = ApiClient("fixture", ApiTransport { path, _, _, _ ->
                if (path.endsWith("/play-servers")) {
                    requested.complete(Unit)
                    release.await()
                    """[{"play_id":"fixture","play_url":"https://example.test"}]"""
                } else """{"id":1,"title":"Fixture"}"""
            })
            val model = MovieDetailModel(MediaReference(MediaKind.MOVIE, 1), api)
            val loading = launch { model.load() }
            requested.await()
            assertNull(model.movie)
            release.complete(Unit)
            loading.join()
            assertEquals("Fixture", model.movie?.title)
            assertTrue(model.canPlay)
        }
    }

    @Test fun castAndCollectionsAppendPagesWithoutDuplicates() = runBlocking {
        withContext(Dispatchers.Main) {
            val api = ApiClient("fixture", ApiTransport { path, _, query, _ ->
                val more = query.any { it.first == "cursor" && it.second == "next" }
                val records = JSONArray()
                (if (more) listOf(2, 3) else listOf(1, 2)).forEach { id ->
                    records.put(if (path.endsWith("/cast")) JSONObject().put("person", JSONObject().put("id", id).put("name", "Actor $id"))
                    else JSONObject().put("id", id).put("title", "Movie $id"))
                }
                JSONObject().put("records", records).put("cursor", if (more) JSONObject.NULL else "next").toString()
            })
            val cast = CastRowModel(MediaReference(MediaKind.MOVIE, 1), api)
            cast.load(); cast.load(more = true)
            assertEquals(listOf(1, 2, 3), cast.members.map { it.id })
            assertNull(cast.cursor)
            val collection = MovieCollectionModel(MovieCollection(1, "Collection"), api)
            collection.load(); collection.load(more = true)
            assertEquals(listOf(1, 2, 3), collection.movies.map { it.id })
            assertNull(collection.cursor)
        }
    }
}
