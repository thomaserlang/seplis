package net.seplis.tv

import android.view.KeyEvent
import androidx.compose.ui.test.*
import org.junit.Test

class ProfileMenuUITests : UITestCase() {
    @Test fun cancellingAddAccountRestoresProfileMenuAndTab() {
        compose.waitUntil(10_000) {
            compose.onAllNodesWithContentDescription("National Treasure").fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithText("Series").performClick()
        awaitText("Available")
        compose.onNodeWithText("Alex").performClick()
        compose.onNodeWithText("Add Account").performClick()
        compose.waitUntil(10_000) { compose.onAllNodesWithContentDescription("Sign-in code 123456").fetchSemanticsNodes().isNotEmpty() }
        key(KeyEvent.KEYCODE_BACK)
        compose.onNodeWithText("Add Account").assertIsFocused()

        key(KeyEvent.KEYCODE_DPAD_CENTER)
        compose.waitUntil(10_000) { compose.onAllNodesWithContentDescription("Sign-in code 123456").fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithText("Back to accounts").performClick()
        compose.onNodeWithText("Add Account").assertIsFocused()
        key(KeyEvent.KEYCODE_BACK)
        compose.onNodeWithText("Series").assertIsFocused()
        compose.onNodeWithText("Alex").assertIsDisplayed()
        compose.onNodeWithText("Available").assertIsDisplayed()
    }

    @Test fun profileMenuFocusesActiveAccountAndRemovesOnlyOtherAccounts() {
        awaitText("Alex")
        compose.onNodeWithText("Alex").performClick()
        compose.onNodeWithText("Sam").performClick()
        awaitText("Sam")
        compose.onNodeWithText("Sam").performClick()
        compose.onAllNodesWithText("Sam").onLast().assertIsFocused()
        compose.onNodeWithText("Sign Out of Sam").assertIsDisplayed()
        compose.onNodeWithText("Remove an Account").performClick()
        compose.onNode(hasText("Alex") and hasAnyAncestor(hasTestTag("profiles-panel"))).assertIsDisplayed()
        compose.onNode(hasText("Sam") and hasAnyAncestor(hasTestTag("profiles-panel"))).assertDoesNotExist()
        key(KeyEvent.KEYCODE_BACK)
        compose.onNodeWithText("Remove an Account").assertIsFocused()
    }
}
