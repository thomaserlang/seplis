package net.seplis.tv

import kotlinx.coroutines.*
import net.seplis.tv.features.playback.PlayRequest
import net.seplis.tv.features.playback.PlaySource
import net.seplis.tv.features.playback.collectPlaySources
import net.seplis.tv.features.playback.resolvePlayUrl
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test

class PlayServerTests {
    private val requests = listOf(PlayRequest("fast", "https://fast.example"), PlayRequest("slow", "https://slow.example"))
    private val source = PlaySource(0, 2_000_000.0, "1080p", "h264", 1920, 1080, 120.0,
        emptyList(), emptyList(), null, null, null, null)

    @Test fun availableSourcesSkipSlowServerAfterGracePeriod() = runBlocking {
        val started = mutableSetOf<String>()
        val cancelled = mutableSetOf<String>()
        val start = System.nanoTime()
        val candidates = withTimeout(5_000) {
            collectPlaySources(requests) { request ->
                started += request.playId
                if (request.playId == "slow") {
                    try { delay(30_000) }
                    catch (error: CancellationException) { cancelled += request.playId; throw error }
                }
                listOf(source)
            }
        }
        assertEquals(listOf("fast"), candidates.map { it.request.playId })
        assertEquals(setOf("fast", "slow"), started)
        assertEquals(setOf("slow"), cancelled)
        assertTrue((System.nanoTime() - start) / 1_000_000 >= 1_800)
    }

    @Test fun firstUsableResponseAfterGracePeriodSkipsPendingServer() = runBlocking {
        val cancelled = mutableSetOf<String>()
        val candidates = withTimeout(5_000) {
            collectPlaySources(requests) { request ->
                try { delay(if (request.playId == "fast") 2_200 else 30_000) }
                catch (error: CancellationException) { cancelled += request.playId; throw error }
                listOf(source)
            }
        }
        assertEquals(listOf("fast"), candidates.map { it.request.playId })
        assertEquals(setOf("slow"), cancelled)
    }

    @Test fun emptyResponseDoesNotEndDiscoveryAtGracePeriod() = runBlocking {
        val candidates = withTimeout(5_000) {
            collectPlaySources(requests) { request ->
                if (request.playId == "fast") emptyList() else {
                    delay(2_200)
                    listOf(source)
                }
            }
        }
        assertEquals(listOf("slow"), candidates.map { it.request.playId })
    }

    @Test fun completedDiscoveryPreservesServerOrderWithoutWaitingForGracePeriod() = runBlocking {
        val candidates = withTimeout(1_000) {
            collectPlaySources(requests) { request ->
                if (request.playId == "slow") delay(50)
                listOf(source)
            }
        }
        assertEquals(listOf("slow", "fast"), candidates.map { it.request.playId })
    }

    @Test fun cancellingDiscoveryCancelsEveryPendingRequest() = runBlocking {
        val started = mutableSetOf<String>()
        val cancelled = mutableSetOf<String>()
        val discovery = launch {
            collectPlaySources(requests) { request ->
                started += request.playId
                try { delay(30_000) }
                catch (error: CancellationException) { cancelled += request.playId; throw error }
                emptyList()
            }
        }
        withTimeout(1_000) {
            while (started.size < requests.size) yield()
            discovery.cancelAndJoin()
        }
        assertEquals(setOf("fast", "slow"), cancelled)
        assertTrue(discovery.isCancelled)
    }

    @Test fun allEmptyResponsesReportServersWithoutWaitingForGracePeriod() = runBlocking {
        try {
            withTimeout(1_000) { collectPlaySources(requests) { emptyList() } }
            fail("Expected unavailable sources")
        } catch (error: IllegalStateException) {
            assertTrue(error.message!!.contains("fast.example: no media files were returned."))
            assertTrue(error.message!!.contains("slow.example: no media files were returned."))
        }
    }

    @Test fun playServerPathsStayUnderMountPoint() {
        assertEquals("https://play.example.com/mount/session/stream.m3u8",
            resolvePlayUrl("https://play.example.com/mount", "/session/stream.m3u8"))
        assertEquals("https://other.example.com/media.m3u8",
            resolvePlayUrl("https://play.example.com/mount", "https://other.example.com/media.m3u8"))
    }
}
