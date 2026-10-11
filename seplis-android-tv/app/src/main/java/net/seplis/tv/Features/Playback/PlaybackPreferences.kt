package net.seplis.tv.features.playback

import android.content.Context
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.core.networking.text
import org.json.JSONObject

class PlaybackPreferences(context: Context, profileId: String, private val api: APIClient,
    private val seriesPath: String?, private val scope: CoroutineScope) {
    var error by mutableStateOf<String?>(null)
    private var seriesAudio: String? = null
    private var seriesSubtitle: String? = null
    private var pending: Job? = null
    private val store = context.getSharedPreferences("playback_$profileId", Context.MODE_PRIVATE)
    var maxBitrate: Int
        get() = store.getInt("max_bitrate", PlaybackQuality.maximum).takeIf { it in PlaybackQuality.options }
            ?: PlaybackQuality.maximum
        set(value) { store.edit().putInt("max_bitrate", value).apply() }
    var hdrEnabled: Boolean
        get() = store.getBoolean("hdr", true)
        set(value) { store.edit().putBoolean("hdr", value).apply() }
    var audioKey: String?
        get() = seriesAudio ?: store.getString("audio_key", null)
        set(value) { store.edit().putString("audio_key", value).apply() }
    var subtitleKey: String?
        get() = seriesSubtitle ?: store.getString("subtitle_key", null)
        set(value) { store.edit().putString("subtitle_key", value).apply() }
    var subtitlesOff: Boolean
        get() = seriesSubtitle == null && store.getBoolean("subtitles_off", false)
        set(value) { store.edit().putBoolean("subtitles_off", value).apply() }

    companion object { val bitrateOptions get() = PlaybackQuality.options }

    suspend fun load() {
        if (seriesPath == null) return
        try {
            val settings = api.objectAt("$seriesPath/user-settings")
            seriesAudio = settings.text("audio_lang")
            seriesSubtitle = settings.text("subtitle_lang")
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) {
            error = "Series playback preferences could not be loaded. Using this profile's saved defaults."
        }
    }

    fun saveAudio(key: String) {
        audioKey = key
        seriesAudio = key
        save("audio_lang", key)
    }

    fun saveSubtitle(key: String?) {
        subtitleKey = key
        subtitlesOff = key == null
        seriesSubtitle = key
        save("subtitle_lang", key)
    }

    private fun save(field: String, value: String?) {
        if (seriesPath == null) return
        val previous = pending
        pending = scope.launch {
            previous?.join()
            try { api.perform("$seriesPath/user-settings", "PUT", JSONObject().put(field, value ?: JSONObject.NULL)) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (failure: Exception) { error = "Playback preferences were saved on this TV but could not be synced to Seplis." }
        }
    }

    suspend fun flush() { pending?.join() }
}
