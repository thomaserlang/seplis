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

class CastRowTests {
    @Test fun castAppendsPagesWithoutDuplicates() = runBlocking {
        withContext(Dispatchers.Main) {
            val api = APIClient("fixture", ApiTransport { _, _, query, _ ->
                val more = query.any { it.first == "cursor" && it.second == "next" }
                val records = JSONArray()
                (if (more) listOf(2, 3) else listOf(1, 2)).forEach { id ->
                    records.put(JSONObject().put("person", JSONObject().put("id", id).put("name", "Actor $id")))
                }
                JSONObject().put("records", records).put("cursor", if (more) JSONObject.NULL else "next").toString()
            })
            val cast = CastRowModel(MediaReference(MediaKind.MOVIE, 1), api)
            cast.load(); cast.load(more = true)
            assertEquals(listOf(1, 2, 3), cast.members.map { it.id })
            assertNull(cast.cursor)
        }
    }
}
