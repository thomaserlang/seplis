package net.seplis.tv

import androidx.compose.runtime.*
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.v2.createComposeRule
import kotlinx.coroutines.CompletableDeferred
import net.seplis.tv.app.AppView
import net.seplis.tv.core.networking.*
import net.seplis.tv.debug.UITestFixtures
import net.seplis.tv.features.home.*
import net.seplis.tv.features.library.*
import net.seplis.tv.features.search.*
import net.seplis.tv.features.topshelf.TopShelfLink
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import java.util.concurrent.atomic.AtomicInteger

class BrowsingUITests {
    @get:Rule val compose = createComposeRule()

    @Test fun coldLaunchLinkWaitsForProfileRestoration() {
        val session = UITestFixtures.session()
        var link by mutableStateOf<TopShelfLink?>(TopShelfLink(1, MediaReference(MediaKind.SERIES, 1), null, false))
        compose.setContent { AppView(session, link) { link = null } }
        compose.waitUntil(5_000) { link == null }
        compose.waitUntil(5_000) { compose.onAllNodesWithText("Season 1").fetchSemanticsNodes().isNotEmpty() }
        assertNull(session.error)
    }

    @Test fun searchDoesNotShowEmptyResultsUntilTheRequestFinishes() {
        val release = CompletableDeferred<Unit>()
        val model = SearchModel(ApiClient("fixture", ApiTransport { _, _, _, _ -> release.await(); "[]" }))
        model.query = "Fixture"
        compose.setContent { SearchView(model, 0, 0, {}, {}) }
        compose.waitUntil(5_000) { model.isLoading }
        compose.onNodeWithText("No results for \"Fixture\"").assertDoesNotExist()
        release.complete(Unit)
        compose.waitUntil(5_000) { model.loadedQuery == "Fixture" }
        compose.onNodeWithText("No results for \"Fixture\"").assertIsDisplayed()
    }

    @Test fun homeRefreshesWhenItBecomesActiveAgain() {
        val requests = AtomicInteger()
        val store = HomeStore(ApiClient("fixture", ApiTransport { path, _, _, _ ->
            if (path == "users/me/watched") {
                val version = requests.incrementAndGet()
                """{"records":[{"type":"movie","data":{"id":1,"title":"Version $version"}}]}"""
            } else """{"records":[]}"""
        }))
        var active by mutableStateOf(true)
        compose.setContent { HomeView(store, 0, 0, {}, {}, isActive = active) }
        compose.waitUntil(5_000) { store.shelf(HomeShelf.WATCHED).items.firstOrNull()?.media?.title == "Version 1" }
        compose.runOnIdle { active = false }
        compose.waitForIdle()
        compose.runOnIdle { active = true }
        compose.waitUntil(5_000) { store.shelf(HomeShelf.WATCHED).items.firstOrNull()?.media?.title == "Version 2" }
        assertEquals(2, requests.get())
    }
}
