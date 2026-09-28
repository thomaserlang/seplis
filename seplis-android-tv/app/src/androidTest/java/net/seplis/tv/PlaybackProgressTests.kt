package net.seplis.tv

import kotlinx.coroutines.*
import net.seplis.tv.core.networking.*
import net.seplis.tv.features.playback.PlaybackProgress
import org.junit.Assert.*
import org.junit.Test

class PlaybackProgressTests {
    @Test fun progressFailureIsDiagnosticAndCompletionIsNotRetried() = runBlocking {
        withContext(Dispatchers.Main) {
            val calls = mutableListOf<String>()
            val api = APIClient("fixture", ApiTransport { path, _, _, _ -> calls += path; throw APIError(503, "Offline") })
            val progress = PlaybackProgress(api, "movies/1", this, 0)
            progress.record(10_000, 100_000)
            progress.finish()
            progress.finish()
            progress.savePosition(20_000)
            progress.flush()
            assertEquals(listOf("movies/1/watched-position", "movies/1/watched"), calls)
            assertTrue(progress.completed)
            assertNotNull(progress.error)
        }
    }
}
