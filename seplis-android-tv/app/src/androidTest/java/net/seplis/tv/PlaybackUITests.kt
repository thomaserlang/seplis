package net.seplis.tv

import android.view.KeyEvent
import android.view.View
import androidx.compose.ui.test.*
import androidx.media3.common.Player
import androidx.media3.ui.PlayerControlView
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@androidx.annotation.OptIn(androidx.media3.common.util.UnstableApi::class)
class PlaybackUITests : UITestCase() {
    private val controls get() = compose.activity.findViewById<PlayerControlView>(androidx.media3.ui.R.id.exo_controller)

    @Before fun resetFixturePreferences() {
        check(BuildConfig.USE_FIXTURES)
        compose.activity.getSharedPreferences("playback_1", 0).edit().clear().commit()
    }

    private fun awaitReady() {
        compose.waitUntil(15_000) {
            var ready = false
            compose.runOnIdle { ready = controls?.player?.playbackState == Player.STATE_READY }
            ready
        }
    }

    private fun openMovie() {
        compose.waitUntil(10_000) {
            compose.onAllNodesWithContentDescription("National Treasure").fetchSemanticsNodes().isNotEmpty()
        }
        compose.onAllNodesWithContentDescription("National Treasure").onFirst().performClick()
        awaitText("Play")
        compose.onNodeWithText("Play").performClick()
        awaitReady()
    }

    private fun nativeAction(id: Int) {
        compose.runOnIdle {
            controls.show()
        }
        compose.waitForIdle()
        compose.runOnIdle {
            assertTrue(controls.isFullyVisible)
            assertTrue(compose.activity.findViewById<View>(id).requestFocus())
        }
        key(KeyEvent.KEYCODE_DPAD_CENTER)
    }

    private fun awaitPlayer(condition: (Player) -> Boolean) {
        compose.waitUntil(15_000) {
            var matches = false
            compose.runOnIdle { matches = controls?.player?.let(condition) == true }
            matches
        }
    }

    @Test fun videoPlaysPausesSeeksAndQualityChangePreservesPosition() {
        openMovie()
        compose.waitUntil(10_000) {
            var moving = false
            compose.runOnIdle { moving = controls.player!!.currentPosition > 1000 && controls.player!!.isPlaying }
            moving
        }
        key(KeyEvent.KEYCODE_MEDIA_PAUSE)
        awaitPlayer { !it.playWhenReady }
        compose.runOnIdle { controls.hide() }
        compose.waitForIdle()
        key(KeyEvent.KEYCODE_DPAD_UP)
        compose.runOnIdle { assertTrue(controls.isFullyVisible) }
        compose.runOnIdle { assertFalse(controls.player!!.playWhenReady) }
        key(KeyEvent.KEYCODE_MEDIA_FAST_FORWARD)
        compose.runOnIdle { assertTrue(controls.player!!.currentPosition >= 10_000) }
        nativeAction(androidx.media3.ui.R.id.exo_settings)
        compose.onNodeWithText("Quality").performScrollTo().performClick()
        compose.onNodeWithText("20 Mbps").performClick()
        awaitReady()
        compose.runOnIdle {
            assertTrue(controls.player!!.currentPosition >= 10_000)
            assertFalse(controls.player!!.playWhenReady)
        }
        key(KeyEvent.KEYCODE_BACK)
        awaitText("National Treasure")
    }

    @Test fun nativeSettingsInfoMenusScrollAndReturnToTransport() {
        openMovie()
        nativeAction(androidx.media3.ui.R.id.exo_settings)
        compose.onNodeWithText("Subtitles").assertDoesNotExist()
        compose.onNodeWithText("Playback Decision").performClick()
        compose.onNodeWithText("Delivery").assertIsDisplayed()
        compose.onNodeWithText("HLS stream").assertIsDisplayed()
        key(KeyEvent.KEYCODE_BACK)
        compose.onNodeWithText("Media Info").performScrollTo().performClick()
        compose.onNodeWithText("Audio language").performScrollTo().assertIsDisplayed()
        key(KeyEvent.KEYCODE_BACK)
        key(KeyEvent.KEYCODE_BACK)
        compose.runOnIdle {
            assertTrue(compose.activity.findViewById<View>(androidx.media3.ui.R.id.exo_settings).hasFocus())
        }
    }

    @Test fun nextEpisodeUsesTheNativeTransportAction() {
        compose.waitUntil(10_000) {
            compose.onAllNodesWithContentDescription("NCIS").fetchSemanticsNodes().isNotEmpty()
        }
        compose.onAllNodesWithContentDescription("NCIS").onFirst().performClick()
        awaitText("Rewatch")
        compose.onNodeWithText("Rewatch").performClick()
        awaitReady()
        nativeAction(R.id.playback_next_episode)
        awaitPlayer { it.mediaMetadata.subtitle.toString() == "S1 E2 - Hung Out to Dry" }
        awaitReady()
        compose.runOnIdle {
            assertEquals("S1 E2 - Hung Out to Dry", controls.player!!.mediaMetadata.subtitle.toString())
            assertTrue(controls.player!!.currentPosition < 10_000)
        }
    }

    @Test fun episodeListRestoresThePlayedEpisodeAfterClosingPlayer() {
        compose.waitUntil(10_000) {
            compose.onAllNodesWithContentDescription("NCIS").fetchSemanticsNodes().isNotEmpty()
        }
        compose.onAllNodesWithContentDescription("NCIS").onFirst().performClick()
        awaitText("Season 1")
        compose.onNodeWithText("Season 1").performScrollTo().performClick()
        awaitText("Hung Out to Dry")
        compose.onNodeWithText("Play").performScrollTo()
            .performSemanticsAction(androidx.compose.ui.semantics.SemanticsActions.RequestFocus)
        key(KeyEvent.KEYCODE_DPAD_CENTER)
        awaitReady()
        key(KeyEvent.KEYCODE_BACK)
        awaitText("Hung Out to Dry")
        compose.onNode(hasText("Play") or hasText("Resume")).assertIsFocused()
    }
}
