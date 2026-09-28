package net.seplis.tv.features.topshelf

import android.content.ContentUris
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.media.tv.TvContract.WatchNextPrograms as Programs
import android.net.Uri
import android.util.Log
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.channels.BufferOverflow
import net.seplis.tv.app.MainActivity
import net.seplis.tv.core.networking.*
import net.seplis.tv.features.library.*
import net.seplis.tv.features.series.Episode

object WatchHistory {
    private val notifications = MutableSharedFlow<Unit>(extraBufferCapacity = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST)
    val changes = notifications.asSharedFlow()
    fun notifyChanged() { notifications.tryEmit(Unit) }
}

data class TopShelfEntry(val link: TopShelfLink, val title: String, val poster: String,
    val position: Int, val duration: Int) {
    val key get() = "${link.accountID}:${link.reference.path}"
}

interface TopShelfStore {
    fun clearOtherAccounts(accountID: Int?)
    fun replace(entries: List<TopShelfEntry>)
}

class TopShelfPublisher(private val store: TopShelfStore) {
    private val publishLock = Mutex()
    suspend fun refresh(api: ApiClient?, accountID: Int?) {
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

class AndroidTopShelfStore(private val context: Context) : TopShelfStore {
    private val resolver get() = context.contentResolver
    private fun existing(): Map<String, Long> = buildMap {
        resolver.query(Programs.CONTENT_URI, arrayOf(Programs._ID, Programs.COLUMN_INTERNAL_PROVIDER_ID,
            Programs.COLUMN_PACKAGE_NAME), null, null, null)?.use { cursor ->
            while (cursor.moveToNext()) {
                if (cursor.getString(2) == context.packageName) cursor.getString(1)?.let { put(it, cursor.getLong(0)) }
            }
        }
    }
    private fun remove(id: Long) { resolver.delete(ContentUris.withAppendedId(Programs.CONTENT_URI, id), null, null) }
    override fun clearOtherAccounts(accountID: Int?) {
        existing().filterKeys { accountID == null || !it.startsWith("$accountID:") }.values.forEach(::remove)
    }
    override fun replace(entries: List<TopShelfEntry>) {
        val old = existing()
        old.filterKeys { key -> entries.none { it.key == key } }.values.forEach(::remove)
        val now = System.currentTimeMillis()
        entries.forEachIndexed { index, entry ->
            val intent = Intent(context, MainActivity::class.java).setAction(Intent.ACTION_VIEW).setData(entry.link.uri)
            val values = ContentValues().apply {
                put(Programs.COLUMN_INTERNAL_PROVIDER_ID, entry.key)
                put(Programs.COLUMN_TITLE, entry.title)
                put(Programs.COLUMN_POSTER_ART_URI, entry.poster)
                put(Programs.COLUMN_POSTER_ART_ASPECT_RATIO, Programs.ASPECT_RATIO_2_3)
                put(Programs.COLUMN_INTENT_URI, intent.toUri(Intent.URI_INTENT_SCHEME))
                put(Programs.COLUMN_TYPE, if (entry.link.reference.kind == MediaKind.MOVIE) Programs.TYPE_MOVIE else Programs.TYPE_TV_EPISODE)
                put(Programs.COLUMN_WATCH_NEXT_TYPE, if (entry.position > 0) Programs.WATCH_NEXT_TYPE_CONTINUE else Programs.WATCH_NEXT_TYPE_NEXT)
                put(Programs.COLUMN_LAST_PLAYBACK_POSITION_MILLIS, entry.position * 1000L)
                put(Programs.COLUMN_DURATION_MILLIS, entry.duration * 1000L)
                put(Programs.COLUMN_LAST_ENGAGEMENT_TIME_UTC_MILLIS, now - index)
            }
            val id = old[entry.key]
            if (id == null) resolver.insert(Programs.CONTENT_URI, values)
            else resolver.update(ContentUris.withAppendedId(Programs.CONTENT_URI, id), values, null, null)
        }
    }
}
