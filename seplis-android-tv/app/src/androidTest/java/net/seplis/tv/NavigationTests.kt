package net.seplis.tv

import android.view.KeyEvent
import androidx.compose.ui.test.*
import org.junit.Test
import androidx.test.platform.app.InstrumentationRegistry
import net.seplis.tv.app.MainActivity

class NavigationTests : UITestCase() {
    @Test fun remoteTabsAndProfileDismissalRestoreMenuFocus() {
        compose.waitUntil(10_000) {
            compose.onAllNodesWithContentDescription("National Treasure").fetchSemanticsNodes().isNotEmpty()
        }
        key(KeyEvent.KEYCODE_BACK)
        compose.onNodeWithText("Home").assertIsFocused()
        key(KeyEvent.KEYCODE_DPAD_RIGHT)
        key(KeyEvent.KEYCODE_DPAD_DOWN)
        awaitText("Available")
        compose.onNodeWithText("Filters").assertIsFocused()
        key(KeyEvent.KEYCODE_BACK)
        compose.onNodeWithText("Series").assertIsFocused()
        compose.onNodeWithText("Alex").performClick()
        awaitText("Add Account")
        key(KeyEvent.KEYCODE_BACK)
        compose.onNodeWithText("Series").assertIsFocused()
    }

    @Test fun launcherLinksRejectOtherAccountsAndOpenOwnedDetails() {
        val launchIntent = android.content.Intent(compose.activity.intent)
        try {
            awaitText("Alex")
            compose.runOnIdle { InstrumentationRegistry.getInstrumentation().callActivityOnNewIntent(compose.activity,
                android.content.Intent(compose.activity, MainActivity::class.java)
                .setAction(android.content.Intent.ACTION_VIEW)
                .setData(android.net.Uri.parse("seplis://top-shelf/movie/1?account=2&action=details"))) }
            awaitText("Switch to the profile that owns this Continue Watching item, then select it again.")
            compose.onNodeWithText("OK").performClick()
            compose.runOnIdle { InstrumentationRegistry.getInstrumentation().callActivityOnNewIntent(compose.activity,
                android.content.Intent(compose.activity, MainActivity::class.java)
                .setAction(android.content.Intent.ACTION_VIEW)
                .setData(android.net.Uri.parse("seplis://top-shelf/movie/1?account=1&action=details"))) }
            awaitText("IMDB")
            compose.onNodeWithText("National Treasure").assertIsDisplayed()
        } finally {
            // ActivityScenario matches lifecycle events against its original launch intent.
            compose.runOnIdle { compose.activity.intent = launchIntent }
        }
    }
}
