package net.seplis.tv.features.playback

import android.net.Uri
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.selects.select
import org.json.JSONArray
import org.json.JSONObject
import net.seplis.tv.core.networking.HttpClient
import okhttp3.Request
import java.util.UUID

interface PlayServer {
    suspend fun sources(requests: List<PlayRequest>): List<PlayCandidate>
    suspend fun open(candidate: PlayCandidate, capabilities: PlaybackCapabilities,
        audioKey: String?, subtitleKey: String?, forceTranscode: Boolean,
        compatibilityFallback: Boolean = false): PlaySession
    suspend fun keepAlive(session: PlaySession)
    suspend fun close(session: PlaySession)
}

class PlayServerClient : PlayServer {
    override suspend fun sources(requests: List<PlayRequest>): List<PlayCandidate> =
        collectPlaySources(requests) { request ->
            val url = buildUrl(request.url, "sources", mapOf("play_id" to request.playId))
            JSONArray(fetch(url, timeoutMs = 20_000)).let { array ->
                (0 until array.length()).map { PlaySource.from(array.getJSONObject(it)) }
            }
        }

    override suspend fun open(candidate: PlayCandidate, capabilities: PlaybackCapabilities,
        audioKey: String?, subtitleKey: String?, forceTranscode: Boolean,
        compatibilityFallback: Boolean): PlaySession {
        val query = capabilities.query(forceTranscode, compatibilityFallback) + mapOf(
            "play_id" to candidate.request.playId, "source_index" to candidate.source.index.toString(),
            "session" to UUID.randomUUID().toString()) +
            (audioKey?.let { mapOf("audio_lang" to it) } ?: emptyMap()) +
            (subtitleKey?.let { mapOf("hls_subtitle_lang" to it) } ?: emptyMap())
        return JSONObject(fetch(buildUrl(candidate.request.url, "request-media", query)))
            .playSession(candidate.request.url)
    }

    override suspend fun keepAlive(session: PlaySession) { fetch(session.keepAliveUrl, timeoutMs = 5_000) }
    override suspend fun close(session: PlaySession) { runCatching { fetch(session.closeUrl, timeoutMs = 5_000) } }

    private fun buildUrl(base: String, path: String, query: Map<String, String>): String {
        val builder = Uri.parse(base.trimEnd('/') + "/" + path).buildUpon()
        query.forEach { (key, value) -> builder.appendQueryParameter(key, value) }
        return builder.build().toString()
    }

    private suspend fun fetch(url: String, timeoutMs: Int = 30_000): String {
        check(!net.seplis.tv.BuildConfig.USE_FIXTURES) { "Fixture builds cannot use a live play server" }
        require(url.startsWith("https://") || url.startsWith("http://"))
        val response = try { HttpClient.request(Request.Builder().url(url).build(), timeoutMs.toLong()) }
        catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: java.io.IOException) { throw PlayServerFailure(null, PlayServerFailure.message(failure), failure) }
        if (response.status !in 200..299)
            throw PlayServerFailure(response.status)
        return response.body
    }
}

private data class SourceResponse(val index: Int, val candidates: List<PlayCandidate>, val failure: String?)

internal suspend fun collectPlaySources(
    requests: List<PlayRequest>,
    loadSources: suspend (PlayRequest) -> List<PlaySource>
): List<PlayCandidate> = coroutineScope {
    ensureActive()
    check(requests.isNotEmpty()) { "No play server has this title available for your account." }
    val timer = async { delay(2_000) }
    val pending = requests.reversed().mapIndexed { index, request ->
        async {
            val host = runCatching { java.net.URI(request.url).host }.getOrNull() ?: "Play server"
            try {
                val sources = loadSources(request)
                SourceResponse(index, sources.map { PlayCandidate(request, it) },
                    if (sources.isEmpty()) "$host: no media files were returned." else null)
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (error: Exception) {
                SourceResponse(index, emptyList(), "$host: ${PlayServerFailure.message(error)}")
            }
        }
    }.toMutableList()
    try {
        val responses = mutableListOf<SourceResponse>()
        var gracePeriodElapsed = false
        while (pending.isNotEmpty()) {
            val completed = select {
                if (!gracePeriodElapsed) timer.onAwait { null }
                pending.forEach { worker ->
                    worker.onAwait { response ->
                        responses += response
                        worker
                    }
                }
            }
            if (completed == null) gracePeriodElapsed = true else pending.remove(completed)
            ensureActive()
            if (gracePeriodElapsed && responses.any { it.candidates.isNotEmpty() }) break
        }
        responses.sortBy { it.index }
        val candidates = responses.flatMap { it.candidates }
        check(candidates.isNotEmpty()) { responses.mapNotNull { it.failure }.joinToString("\n") }
        candidates
    } finally {
        timer.cancel()
        pending.forEach { it.cancel() }
    }
}
