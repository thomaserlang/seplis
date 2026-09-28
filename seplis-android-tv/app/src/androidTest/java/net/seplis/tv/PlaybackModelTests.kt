package net.seplis.tv

import androidx.test.platform.app.InstrumentationRegistry
import kotlinx.coroutines.*
import net.seplis.tv.core.networking.*
import net.seplis.tv.debug.PlaybackInfoFixture
import net.seplis.tv.features.library.*
import net.seplis.tv.features.playback.*
import net.seplis.tv.features.series.Episode
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

class PlaybackModelTests {
    private val context get() = InstrumentationRegistry.getInstrumentation().targetContext
    private val fixture = PlaybackInfoFixture()
    private val api = ApiClient("fixture", ApiTransport { path, _, _, _ -> when {
        path.endsWith("/play-servers") -> """[{"play_id":"$path","play_url":"https://example.test"}]"""
        path.endsWith("/episodes/2") -> """{"number":2,"title":"Next"}"""
        else -> "{}"
    } })

    private suspend fun await(condition: () -> Boolean) {
        withTimeout(15_000) { while (!condition()) delay(25) }
    }

    @Test fun changingAudioRecalculatesAutomaticSubtitles() = runBlocking {
        withContext(Dispatchers.Main) {
            context.getSharedPreferences("playback_model-tests", 0).edit().clear().commit()
            val locales = android.os.LocaleList.getDefault()
            android.os.LocaleList.setDefault(android.os.LocaleList(java.util.Locale.ENGLISH))
            val model = PlaybackModel(context, PlaybackTarget(MediaReference(MediaKind.MOVIE, 1), "Fixture"), api, "model-tests", {}, fixture)
            try {
                model.start()
                await { !model.isLoading }
                assertNull(model.error)
                assertEquals("jpn:1", model.selectedAudio)
                assertEquals("eng:0", model.selectedSubtitle)
                model.selectAudio("eng:0")
                await { !model.isLoading }
                assertNull(model.selectedSubtitle)
                model.selectAudio("jpn:1")
                await { !model.isLoading }
                assertEquals("eng:0", model.selectedSubtitle)
            } finally { model.stop(); model.dispose(); android.os.LocaleList.setDefault(locales) }
        }
    }

    @Test fun unavailableNextEpisodeDoesNotBlockCurrentPlayback() = runBlocking {
        withContext(Dispatchers.Main) {
            var checks = 0
            val server = object : PlayServer by fixture {
                override suspend fun sources(requests: List<PlayRequest>): List<PlayCandidate> {
                    checks++
                    if (requests.first().playId.contains("episodes/2")) throw IllegalStateException("No media files")
                    return fixture.sources(requests)
                }
            }
            val episode = Episode.from(JSONObject("""{"number":1,"title":"First"}"""))
            val model = PlaybackModel(context, PlaybackTarget(MediaReference(MediaKind.SERIES, 1), "Fixture", episode), api, "model-tests", {}, server)
            try {
                model.start()
                await { !model.isLoading }
                assertNull(model.error)
                assertNull(model.nextEpisode)
                assertEquals(2, checks)
            } finally { model.stop(); model.dispose() }
        }
    }

    @Test fun missingServerSessionStopsOnFirstHeartbeat() = runBlocking {
        withContext(Dispatchers.Main) {
            var heartbeats = 0
            val server = object : PlayServer by fixture {
                override suspend fun keepAlive(session: PlaySession) {
                    heartbeats++
                    throw PlayServerFailure(404, "Session expired")
                }
            }
            val model = PlaybackModel(context, PlaybackTarget(MediaReference(MediaKind.MOVIE, 1), "Fixture"), api, "model-tests", {}, server)
            try {
                model.start()
                await { model.error != null }
                assertEquals("The play-server session was lost. Retry to reconnect.", model.error)
                assertEquals(1, heartbeats)
                await { model.player == null && model.session == null }
            } finally { model.stop(); model.dispose() }
        }
    }

    @Test fun closingDuringPreparationCancelsThePendingRequest() = runBlocking {
        withContext(Dispatchers.Main) {
            val started = CompletableDeferred<Unit>()
            val pendingAPI = ApiClient("fixture", ApiTransport { _, _, _, _ ->
                started.complete(Unit)
                awaitCancellation()
            })
            val model = PlaybackModel(context, PlaybackTarget(MediaReference(MediaKind.MOVIE, 1), "Fixture"), pendingAPI, "model-tests", {}, fixture)
            try {
                model.start()
                started.await()
                withTimeout(1_000) { model.stop() }
                assertNull(model.player)
                assertNull(model.session)
            } finally { model.dispose() }
        }
    }

    @Test fun terminalPlayerFailureClosesBothOriginalAndFallbackSessions() = runBlocking {
        withContext(Dispatchers.Main) {
            var opened = 0
            var closed = 0
            val server = object : PlayServer by fixture {
                override suspend fun open(candidate: PlayCandidate, capabilities: PlaybackCapabilities,
                    audioKey: String?, subtitleKey: String?, forceTranscode: Boolean, compatibilityFallback: Boolean): PlaySession {
                    opened++
                    return fixture.open(candidate, capabilities, audioKey, subtitleKey, forceTranscode, compatibilityFallback)
                        .copy(hlsUrl = "file:///android_asset/missing-fixture.mp4")
                }
                override suspend fun close(session: PlaySession) { closed++ }
            }
            val model = PlaybackModel(context, PlaybackTarget(MediaReference(MediaKind.MOVIE, 1), "Fixture"), api, "model-tests", {}, server)
            try {
                model.start()
                await { model.error != null && model.player == null && model.session == null && closed == 2 }
                assertEquals(2, opened)
                assertFalse(model.isLoading)
            } finally { model.stop(); model.dispose() }
        }
    }
}
