package net.seplis.tv

import android.view.KeyEvent
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.test.platform.app.InstrumentationRegistry
import net.seplis.tv.app.*
import net.seplis.tv.core.networking.*
import net.seplis.tv.core.security.*
import org.junit.Rule
import org.junit.Test

class AuthenticationUITests {
    @get:Rule val compose = createComposeRule()

    @Test fun cancellingSignInReturnsToProfileChooser() {
        val store = object : ProfileStore {
            var snapshot = ProfileSnapshot(listOf(Profile(1, "Alex", "fixture"), Profile(2, "Sam", null)))
            override fun load() = snapshot
            override fun save(snapshot: ProfileSnapshot) { this.snapshot = snapshot }
        }
        val session = AppSession(store) { token -> APIClient(token, ApiTransport { path, _, _, _ -> when (path) {
            "device-authorization" -> """{"device_code":"fixture","user_code":"123456","verification_uri":"https://example.test","expires_at":"2099-01-01T00:00:00Z","poll_interval_seconds":3}"""
            "device-authorization/token" -> """{"status":"pending"}"""
            else -> error("Unexpected fixture request: $path")
        } }) }
        compose.setContent { AppView(session) }
        compose.waitUntil(5_000) { compose.onAllNodesWithText("Profiles").fetchSemanticsNodes().isNotEmpty() }
        compose.onNodeWithText("Alex").assertIsFocused()
        compose.onNodeWithText("Sign in again").assertIsDisplayed()
        compose.onNodeWithText("Add Account").performClick()
        compose.waitUntil(5_000) { compose.onAllNodesWithContentDescription("Sign-in code 123456").fetchSemanticsNodes().isNotEmpty() }
        InstrumentationRegistry.getInstrumentation().sendKeyDownUpSync(KeyEvent.KEYCODE_BACK)
        compose.onNodeWithText("Profiles").assertIsDisplayed()
        compose.onNodeWithText("Alex").assertIsDisplayed()
    }
}
