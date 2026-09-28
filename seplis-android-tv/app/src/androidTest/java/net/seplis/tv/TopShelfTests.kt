package net.seplis.tv

import android.net.Uri
import kotlinx.coroutines.runBlocking
import net.seplis.tv.core.networking.*
import net.seplis.tv.features.library.*
import net.seplis.tv.features.topshelf.*
import org.junit.Assert.*
import org.junit.Test

class TopShelfTests {
    @Test fun androidProviderPublishesAndRemovesOnlyFixturePrograms() {
        assertTrue(BuildConfig.USE_FIXTURES)
        val context = androidx.test.platform.app.InstrumentationRegistry.getInstrumentation().targetContext
        val store = AndroidTopShelfStore(context)
        val entry = TopShelfEntry(TopShelfLink(9876, MediaReference(MediaKind.MOVIE, 999999), null, true),
            "SEPLIS fixture", "android.resource://${context.packageName}/${R.drawable.seplis_logo}", 20, 120)
        try {
            store.replace(listOf(entry))
            val keys = mutableListOf<String>()
            context.contentResolver.query(android.media.tv.TvContract.WatchNextPrograms.CONTENT_URI,
                arrayOf(android.media.tv.TvContract.WatchNextPrograms.COLUMN_INTERNAL_PROVIDER_ID,
                    android.media.tv.TvContract.WatchNextPrograms.COLUMN_PACKAGE_NAME), null, null, null)?.use { cursor ->
                while (cursor.moveToNext()) if (cursor.getString(1) == context.packageName) keys += cursor.getString(0)
            }
            assertTrue(keys.contains(entry.key))
            store.replace(listOf(entry.copy(position = 40)))
        } finally { store.clearOtherAccounts(null) }
    }

    @Test fun linksRoundTripAndRejectInvalidPlaybackTargets() {
        val link = TopShelfLink(1, MediaReference(MediaKind.SERIES, 12), 3, true)
        assertEquals(link, TopShelfLink.parse(link.uri))
        assertNull(TopShelfLink.parse(Uri.parse("seplis://top-shelf/series/12?account=1&action=play")))
        assertNull(TopShelfLink.parse(Uri.parse("seplis://top-shelf/movie/12?account=0&action=play")))
        assertNull(TopShelfLink.parse(Uri.parse("https://top-shelf/movie/12?account=1&action=play")))
        assertNull(TopShelfLink.parse(Uri.parse("seplis://top-shelf/movie/12?account=1&action=delete")))
    }

    @Test fun publisherSkipsCompletedMoviesAndClearsPreviousAccount() = runBlocking {
        val cleared = mutableListOf<Int?>()
        var published = emptyList<TopShelfEntry>()
        val store = object : TopShelfStore {
            override fun clearOtherAccounts(accountID: Int?) { cleared += accountID }
            override fun replace(entries: List<TopShelfEntry>) { published = entries }
        }
        val api = ApiClient("fixture", ApiTransport { path, _, _, _ -> when (path) {
            "users/me/watched" -> """{"records":[{"type":"movie","data":{"id":1,"title":"Completed","poster_image":{"url":"https://example.test/1"}}},{"type":"movie","data":{"id":2,"title":"Continue","runtime":100,"poster_image":{"url":"https://example.test/2"}}}]}"""
            "movies/1/watched" -> """{"position":0}"""
            "movies/2/watched" -> """{"position":40}"""
            else -> error(path)
        } })
        val publisher = TopShelfPublisher(store)
        publisher.refresh(api, 7)
        assertEquals(listOf(7), cleared)
        assertEquals(1, published.size)
        assertEquals(2, published.single().link.reference.id)
        assertEquals(7, published.single().link.accountID)
        assertEquals(6000, published.single().duration)
        publisher.refresh(null, null)
        assertNull(cleared.last())
    }
}
