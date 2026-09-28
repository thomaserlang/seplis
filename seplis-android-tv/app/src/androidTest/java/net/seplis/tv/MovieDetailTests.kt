package net.seplis.tv

import kotlinx.coroutines.*
import net.seplis.tv.core.networking.*
import net.seplis.tv.features.library.*
import net.seplis.tv.features.movie.*
import org.junit.Assert.*
import org.junit.Test

class MovieDetailTests {
    @Test fun movieIsNotPublishedBeforePlaybackAvailabilityIsKnown() = runBlocking {
        withContext(Dispatchers.Main) {
            val requested = CompletableDeferred<Unit>()
            val release = CompletableDeferred<Unit>()
            val api = APIClient("fixture", ApiTransport { path, _, _, _ ->
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
}
