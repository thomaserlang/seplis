package net.seplis.tv

import kotlinx.coroutines.*
import net.seplis.tv.core.networking.*
import net.seplis.tv.features.home.*
import org.junit.Assert.*
import org.junit.Test

class HomeShelfTests {
    @Test fun refreshRetainsLoadedPagesAndUsesFreshCursors() = runBlocking {
        withContext(Dispatchers.Main) {
            val cursors = mutableListOf<String?>()
            val model = HomeShelfModel(APIClient("fixture", ApiTransport { _, _, query, _ ->
                val cursor = query.firstOrNull { it.first == "cursor" }?.second
                cursors.add(cursor)
                val records = (if (cursor == null) 1..24 else 25..48)
                    .joinToString(",") { """{"id":$it}""" }
                val next = if (cursor == null) "page-two-${cursors.size}" else "page-three"
                """{"records":[$records],"cursor":"$next"}"""
            }), HomeShelf.POPULAR_MOVIES)
            model.load()
            model.load(more = true)
            val keys = model.items.map { it.key }
            model.load()
            assertEquals(keys, model.items.map { it.key })
            assertEquals(48, model.items.size)
            assertEquals("page-three", model.cursor)
            assertEquals(listOf(null, "page-two-1", null, "page-two-3"), cursors)
        }
    }

    @Test fun laterPageRefreshFailureKeepsEntireLoadedShelf() = runBlocking {
        withContext(Dispatchers.Main) {
            var requests = 0
            val model = HomeShelfModel(APIClient("fixture", ApiTransport { _, _, query, _ ->
                requests++
                if (requests == 4) throw APIError(503, "Offline")
                val more = query.any { it.first == "cursor" }
                val id = if (more) 2 else if (requests == 3) 99 else 1
                val next = if (more) "null" else "\"next\""
                """{"records":[{"id":$id}],"cursor":$next}"""
            }), HomeShelf.POPULAR_MOVIES)
            model.load()
            model.load(more = true)
            model.load()
            assertEquals(listOf(1, 2), model.items.map { it.media.id })
            assertNull(model.cursor)
            assertNotNull(model.error)
            assertFalse(model.loading)
        }
    }
}
