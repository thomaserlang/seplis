package net.seplis.tv.features.playback

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import net.seplis.tv.core.networking.ApiClient
import org.json.JSONObject
import kotlin.math.abs
import kotlin.math.roundToInt

class PlaybackProgress(private val api: ApiClient, private val path: String,
    private val scope: CoroutineScope, start: Long) {
    var completed = false
        private set
    // Diagnostic only. Progress failures must never interrupt playback with an alert.
    var error: String? = null
        private set
    private var lastSaved = start
    private var pending: Job? = null

    fun record(position: Long, duration: Long) {
        if (completed || position < 0 || duration <= 0) return
        if (position >= duration * 0.9) finish()
        else if (abs(position - lastSaved) >= 10_000) savePosition(position)
    }

    fun savePosition(position: Long) {
        if (completed || position < 0) return
        lastSaved = position
        save(position, false)
    }

    fun finish() {
        if (completed) return
        completed = true
        save(lastSaved, true)
    }

    private fun save(position: Long, finished: Boolean) {
        val previous = pending
        pending = scope.launch {
            previous?.join()
            try {
                if (finished) api.perform("$path/watched", "POST")
                else api.perform("$path/watched-position", "PUT", JSONObject()
                    .put("position", (position / 1000.0).roundToInt().coerceAtMost(86400)))
                error = null
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (failure: Exception) { error = failure.message }
        }
    }

    suspend fun flush() { pending?.join() }
}
