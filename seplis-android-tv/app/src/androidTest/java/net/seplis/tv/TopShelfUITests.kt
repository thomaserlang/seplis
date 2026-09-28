package net.seplis.tv

import net.seplis.tv.shared.topshelf.*

import androidx.compose.runtime.*
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.v2.createComposeRule
import net.seplis.tv.app.AppView
import net.seplis.tv.core.networking.*
import net.seplis.tv.debug.UITestFixtures
import net.seplis.tv.features.home.*
import net.seplis.tv.features.library.*
import net.seplis.tv.features.search.*
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

class TopShelfUITests {
    @get:Rule val compose = createComposeRule()

    @Test fun coldLaunchLinkWaitsForProfileRestoration() {
        val session = UITestFixtures.session()
        var link by mutableStateOf<TopShelfLink?>(TopShelfLink(1, MediaReference(MediaKind.SERIES, 1), null, false))
        compose.setContent { AppView(session, link) { link = null } }
        compose.waitUntil(5_000) { link == null }
        compose.waitUntil(5_000) { compose.onAllNodesWithText("Season 1").fetchSemanticsNodes().isNotEmpty() }
        assertNull(session.error)
    }
}
