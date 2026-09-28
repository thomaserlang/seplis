package net.seplis.tv.features.playback

import android.content.Context
import android.net.Uri
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.media3.common.C
import androidx.media3.common.MediaItem
import androidx.media3.common.MediaMetadata
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.series.Episode
import net.seplis.tv.features.library.Watched
import net.seplis.tv.core.networking.text
import org.json.JSONObject

class PlaybackModel(private val context: Context, val target: PlaybackTarget,
    private val api: ApiClient, profileId: String, private val onFinished: () -> Unit,
    private val server: PlayServer = PlayServerClient()) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    val preferences = PlaybackPreferences(context, profileId, api,
        target.reference.path.takeIf { target.episode != null }, scope)
    var player: ExoPlayer? by mutableStateOf(null)
        private set
    var candidates: List<PlayCandidate> by mutableStateOf(emptyList())
        private set
    var selectedSource by mutableStateOf(0)
        private set
    var selectedAudio: String? by mutableStateOf(null)
        private set
    var selectedSubtitle: String? by mutableStateOf(null)
        private set
    var forceTranscode by mutableStateOf(false)
        private set
    var isLoading by mutableStateOf(true)
        private set
    var error: String? by mutableStateOf(null)
        private set
    var nextEpisode: Episode? by mutableStateOf(null)
        private set
    var session: PlaySession? by mutableStateOf(null)
        private set
    private var heartbeat: Job? = null
    private var progressJob: Job? = null
    private var stopped = false
    private var progress: PlaybackProgress? = null
    private var fallback = false
    private var operation: Job? = null
    private var mediaVersion = 0
    private var readyTimeout: Job? = null
    private val openLock = Mutex()

    fun start() {
        if (operation != null) return
        operation = scope.launch {
            try {
                val watched = Watched.from(api.objectAt("${target.path}/watched"))
                val resume = if (target.fromBeginning) 0L else watched.position * 1000L
                progress = PlaybackProgress(api, target.path, scope, resume)
                candidates = server.sources(api.arrayAt("${target.path}/play-servers").let { array ->
                    (0 until array.length()).map { PlayRequest.from(array.getJSONObject(it)) }
                })
                preferences.load()
                selectedSource = PlaybackSourceSelection.preferredIndex(candidates, capabilities()) {
                    PlaybackCapabilities.canPlayMediaType(context, it)
                }
                chooseTracks()
                if (target.episode != null) loadNextEpisode()
                open(resume)
                progressJob = scope.launch { progressLoop() }
            } catch (cancelled: CancellationException) { throw cancelled }
            catch (failure: Exception) {
                fail(failure.message ?: "Playback could not start")
            }
        }
    }

    private fun capabilities() = PlaybackCapabilities.detect(context, preferences.maxBitrate, preferences.hdrEnabled)

    private fun chooseTracks() {
        val source = candidates[selectedSource].source
        selectedAudio = PlaybackLanguages.audio(source, preferences.audioKey)?.key
        selectedSubtitle = if (preferences.subtitlesOff) null else
            PlaybackLanguages.subtitle(source, preferences.subtitleKey,
                source.audio.firstOrNull { it.key == selectedAudio })?.key
    }

    private suspend fun loadNextEpisode() {
        nextEpisode = null
        val episode = target.episode ?: return
        try {
            val path = "${target.reference.path}/episodes/${episode.number + 1}"
            val next = Episode.from(api.objectAt(path))
            val requests = api.arrayAt("$path/play-servers")
            server.sources((0 until requests.length()).map { PlayRequest.from(requests.getJSONObject(it)) })
            nextEpisode = next
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (_: Exception) { nextEpisode = null }
    }

    private suspend fun open(resume: Long, playWhenReady: Boolean = true): Unit = openLock.withLock {
        isLoading = true
        error = null
        val version = ++mediaVersion
        releaseMedia()
        if (stopped) return
        val candidate = candidates[selectedSource]
        val active = server.open(candidate, capabilities(), selectedAudio, selectedSubtitle,
            forceTranscode || fallback, compatibilityFallback = fallback)
        session = active
        heartbeat = scope.launch {
            var failures = 0
            while (true) {
                delay(5_000)
                try { server.keepAlive(active); failures = 0 }
                catch (cancelled: CancellationException) { throw cancelled }
                catch (failure: Exception) {
                    failures++
                    if (failures >= 3 || (failure as? PlayServerFailure)?.statusCode == 404) {
                        fail("The play-server session was lost. Retry to reconnect.")
                        return@launch
                    }
                }
            }
        }
        val replacement = ExoPlayer.Builder(context).setSeekBackIncrementMs(10_000)
            .setSeekForwardIncrementMs(10_000).build()
        replacement.addListener(object : Player.Listener {
            override fun onTracksChanged(tracks: androidx.media3.common.Tracks) {
                if (version != mediaVersion) return
                PlayerSubtitleSelection.apply(replacement,
                    candidate.source.subtitles.firstOrNull { it.key == selectedSubtitle })
            }
            override fun onPlaybackStateChanged(state: Int) {
                if (version != mediaVersion) return
                if (state == Player.STATE_READY) {
                    isLoading = false
                    readyTimeout?.cancel()
                }
                if (state == Player.STATE_ENDED && !stopped) scope.launch {
                    finishProgress()
                    stop()
                    onFinished()
                }
            }
            override fun onPlayerError(failure: PlaybackException) {
                if (stopped || version != mediaVersion) return
                if (!fallback) {
                    fallback = true
                    val position = replacement.currentPosition
                    val playing = replacement.playWhenReady
                    operation = scope.launch {
                        try { open(position, playing) }
                        catch (cancelled: CancellationException) { throw cancelled }
                        catch (problem: Exception) { fail(problem.message ?: "This video could not be played.") }
                    }
                } else { fail(failure.message ?: "This video could not be played.") }
            }
        })
        replacement.trackSelectionParameters = replacement.trackSelectionParameters.buildUpon()
            .setTrackTypeDisabled(C.TRACK_TYPE_TEXT, selectedSubtitle == null)
            .setPreferredTextLanguage(candidate.source.subtitles.firstOrNull { it.key == selectedSubtitle }?.language)
            .build()
        val item = MediaItem.Builder().setUri(Uri.parse(active.hlsUrl))
            .setMediaMetadata(MediaMetadata.Builder().setTitle(target.title)
                .setSubtitle(target.episode?.label).build()).build()
        replacement.setMediaItem(item)
        replacement.prepare()
        if (resume > 0) replacement.seekTo(resume)
        player = replacement
        replacement.playWhenReady = playWhenReady
        readyTimeout = scope.launch {
            delay(45_000)
            if (isLoading && version == mediaVersion) {
                replacement.pause()
                if (!fallback) {
                    fallback = true
                    operation = scope.launch {
                        try { open(resume, playWhenReady) }
                        catch (cancelled: CancellationException) { throw cancelled }
                        catch (failure: Exception) { fail(failure.message ?: "This video could not be played.") }
                    }
                } else {
                    fail("The video did not become ready. Try another source or check the play server.")
                }
            }
        }
    }

    private suspend fun progressLoop() {
        while (!stopped) {
            delay(1_000)
            if (isLoading) continue
            val active = player ?: continue
            val position = active.currentPosition
            val duration = active.duration.takeIf { it > 0 && it != C.TIME_UNSET }
                ?: (candidates.getOrNull(selectedSource)?.source?.duration?.times(1000)?.toLong() ?: 0)
            progress?.record(position, duration)
        }
    }

    private suspend fun finishProgress() {
        progress?.finish()
        progress?.flush()
    }

    fun selectSource(index: Int) {
        if (index !in candidates.indices || index == selectedSource) return
        change {
        selectedSource = index
        fallback = false
        chooseTracks()
        }
    }
    fun selectAudio(key: String) {
        if (key == selectedAudio || candidates.getOrNull(selectedSource)?.source?.audio?.none { it.key == key } != false) return
        change {
        selectedAudio = key
        preferences.saveAudio(key)
        val source = candidates[selectedSource].source
        selectedSubtitle = if (preferences.subtitlesOff) null else PlaybackLanguages.subtitle(
            source, preferences.subtitleKey, source.audio.firstOrNull { it.key == key })?.key
        }
    }
    fun selectSubtitle(key: String?) {
        if (key == selectedSubtitle || stopped || isLoading) return
        if (key != null && candidates.getOrNull(selectedSource)?.source?.subtitles?.none { it.key == key } != false) return
        selectedSubtitle = key
        preferences.saveSubtitle(key)
        val active = player
        val stream = candidates.getOrNull(selectedSource)?.source?.subtitles?.firstOrNull { it.key == key }
        if (active == null || !PlayerSubtitleSelection.apply(active, stream)) change {}
    }
    fun selectBitrate(value: Int) {
        if (value !in PlaybackQuality.options || value == preferences.maxBitrate) return
        change { preferences.maxBitrate = value }
    }
    fun setHDR(value: Boolean) {
        if (value == preferences.hdrEnabled) return
        change { preferences.hdrEnabled = value; fallback = false }
    }
    fun changeForceTranscode(value: Boolean) {
        if (value == forceTranscode) return
        change { forceTranscode = value; fallback = false }
    }

    private fun change(update: () -> Unit) {
        if (stopped || isLoading) return
        val resume = player?.currentPosition ?: 0L
        val playing = player?.playWhenReady ?: true
        isLoading = true
        update()
        operation = scope.launch {
            try { open(resume, playing) }
            catch (cancelled: CancellationException) { throw cancelled }
            catch (failure: Exception) { fail(failure.message ?: "This video could not be played.") }
        }
    }

    private fun fail(message: String) {
        if (stopped) return
        mediaVersion++
        player?.pause()
        progressJob?.cancel()
        heartbeat?.cancel()
        readyTimeout?.cancel()
        error = message
        isLoading = false
        operation = scope.launch { openLock.withLock { releaseMedia() } }
    }

    private suspend fun releaseMedia() {
        readyTimeout?.cancel()
        readyTimeout = null
        heartbeat?.cancel()
        heartbeat = null
        player?.release()
        player = null
        session?.let { active -> session = null; withContext(NonCancellable) { server.close(active) } }
    }

    suspend fun stop() {
        if (stopped) return
        stopped = true
        player?.pause()
        player?.currentPosition?.let { progress?.savePosition(it) }
        operation?.cancelAndJoin()
        progressJob?.cancel()
        progress?.flush()
        net.seplis.tv.features.topshelf.WatchHistory.notifyChanged()
        preferences.flush()
        releaseMedia()
    }

    fun dispose() { scope.launch { stop(); scope.cancel() } }
}
