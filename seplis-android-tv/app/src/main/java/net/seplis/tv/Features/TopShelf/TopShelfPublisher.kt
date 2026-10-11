package net.seplis.tv.features.topshelf

import net.seplis.tv.shared.topshelf.*

import android.media.tv.TvContract.WatchNextPrograms as Programs
import android.util.Log
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.channels.BufferOverflow
import net.seplis.tv.shared.topshelf.*
import net.seplis.tv.core.networking.*
import net.seplis.tv.features.library.*
import net.seplis.tv.features.series.Episode

object WatchHistory {
    private val notifications = MutableSharedFlow<Unit>(extraBufferCapacity = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)
    val changes = notifications.asSharedFlow()
    fun notifyChanged() { notifications.tryEmit(Unit) }
}

class TopShelfPublisher(private val store: TopShelfStore) {
    private val publishLock = Mutex()
    suspend fun refresh(api: APIClient?, accountID: Int?) {
        try {
            withContext(Dispatchers.IO) { publishLock.withLock { store.clearOtherAccounts(accountID) } }
            if (api == null || accountID == null) return
            delay(300)
            val records = api.objectAt("users/me/watched", mapOf("user_can_watch" to "true"))
                .arrayOrEmpty("records").objects()
            val entries = mutableListOf<TopShelfEntry>()
            for (record in records) {
                currentCoroutineContext().ensureActive()
                val media = record.getJSONObject("data")
                val ref = MediaReference(MediaKind.from(record.text("type")), media.getInt("id"))
                val poster = media.poster()?.url ?: continue
                val episode = if (ref.kind == MediaKind.SERIES)
                    api.optionalObject("${ref.path}/episode-to-watch")?.let(Episode::from) else null
                if (ref.kind == MediaKind.SERIES && episode?.canPlay != true) continue
                val position = episode?.watched?.position ?: Watched.from(api.objectAt("${ref.path}/watched")).position
                if (ref.kind == MediaKind.MOVIE && position <= 0) continue
                val title = (media.text("title") ?: "Untitled") + (episode?.let { " - ${it.numberLabel}" } ?: "")
                entries += TopShelfEntry(TopShelfLink(accountID, ref, episode?.number, true), title,
                    if (poster.startsWith("file:")) poster else "$poster@SX640.webp", position,
                    (episode?.runtime ?: media.integer("runtime") ?: 0) * 60)
                if (entries.size == 12) break
            }
            withContext(Dispatchers.IO) { publishLock.withLock { store.replace(entries) } }
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { Log.w("TopShelf", "Could not refresh Watch Next", failure) }
    }
}
