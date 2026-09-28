package net.seplis.tv

import net.seplis.tv.shared.topshelf.*

import androidx.compose.runtime.*
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.v2.createComposeRule
import net.seplis.tv.core.networking.*
import net.seplis.tv.features.home.*
import net.seplis.tv.features.library.*
import net.seplis.tv.features.search.*
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import java.util.concurrent.atomic.AtomicInteger

class HomeUITests {
    @get:Rule val compose = createComposeRule()

    @Test fun homeRefreshesWhenItBecomesActiveAgain() {
        val requests = AtomicInteger()
        val store = HomeViewState(APIClient("fixture", ApiTransport { path, _, _, _ ->
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
