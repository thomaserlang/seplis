package net.seplis.tv

import android.view.KeyEvent
import androidx.compose.ui.test.*
import org.junit.Test

class MediaDetailUITests : UITestCase() {
    private fun openFirstMovie() {
        compose.waitUntil(10_000) {
            compose.onAllNodesWithContentDescription("National Treasure").fetchSemanticsNodes().isNotEmpty()
        }
        compose.onAllNodesWithContentDescription("National Treasure").onFirst().assertIsFocused()
        key(KeyEvent.KEYCODE_DPAD_CENTER)
        awaitText("IMDb".uppercase())
    }

    @Test fun movieFactsWatchedAdjustmentsAndBackFocus() {
        openFirstMovie()
        compose.onNodeWithText("★ 6.9").assertIsDisplayed()
        compose.onNodeWithText("2h 11m").assertIsDisplayed()
        compose.onNodeWithContentDescription("Watched").performClick()
        compose.onNodeWithText("Add another watch").performClick()
        compose.waitUntil(5_000) {
            compose.onAllNodes(SemanticsMatcher.expectValue(
                androidx.compose.ui.semantics.SemanticsProperties.StateDescription, "2 times"))
                .fetchSemanticsNodes().isNotEmpty()
        }
        key(KeyEvent.KEYCODE_BACK)
        compose.onAllNodesWithContentDescription("National Treasure").onFirst().assertIsFocused()
    }

    @Test fun castFocusEntersFirstPortraitAndReturnsToActions() {
        openFirstMovie()
        repeat(3) { key(KeyEvent.KEYCODE_DPAD_RIGHT) }
        compose.onNodeWithText("Favorite").assertIsFocused()
        key(KeyEvent.KEYCODE_DPAD_DOWN)
        compose.onNodeWithContentDescription("Alex Actor, Character 1").assertIsFocused()
        key(KeyEvent.KEYCODE_DPAD_UP)
        compose.onNode(isFocused() and (hasText("Play") or hasContentDescription("Watched") or
            hasText("Watchlist") or hasText("Favorite"))).assertExists()
    }

    @Test fun seriesDefaultFocusAndSeasonBackNavigation() {
        compose.waitUntil(10_000) {
            compose.onAllNodesWithContentDescription("NCIS").fetchSemanticsNodes().isNotEmpty()
        }
        key(KeyEvent.KEYCODE_DPAD_RIGHT)
        key(KeyEvent.KEYCODE_DPAD_CENTER)
        awaitText("Next to watch")
        compose.onNodeWithText("Play").assertIsFocused()
        compose.onNodeWithText("★ 7.8").assertIsDisplayed()
        compose.onNodeWithText("Rewatch").assertIsDisplayed()
        compose.onNodeWithText("Season 1").performScrollTo()
            .performSemanticsAction(androidx.compose.ui.semantics.SemanticsActions.RequestFocus)
        key(KeyEvent.KEYCODE_DPAD_CENTER)
        awaitText("Yankee White")
        compose.onNodeWithText("Hung Out to Dry").assertExists()
        key(KeyEvent.KEYCODE_BACK)
        awaitText("Next to watch")
        compose.onNodeWithText("Season 1").assertIsFocused()
        key(KeyEvent.KEYCODE_BACK)
        compose.onAllNodesWithContentDescription("NCIS").onFirst().assertIsFocused()
    }

    @Test fun collectionNavigationDoesNotReopenCurrentMovie() {
        openFirstMovie()
        compose.onNodeWithContentDescription("National Treasure").assertIsNotEnabled()
        compose.onNodeWithContentDescription("National Treasure: Book of Secrets").performScrollTo().performClick()
        awaitText("2007")
        key(KeyEvent.KEYCODE_BACK)
        awaitText("2004")
        key(KeyEvent.KEYCODE_BACK)
        compose.onAllNodesWithContentDescription("National Treasure").onFirst().assertIsFocused()
    }
}
