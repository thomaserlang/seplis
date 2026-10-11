package net.seplis.tv

import net.seplis.tv.features.library.Watched
import net.seplis.tv.features.playback.PlaybackAction
import org.junit.Assert.assertEquals
import org.junit.Test

class PlaybackActionTests {
    @Test fun playbackActionUsesSavedPositionAndWatchCount() {
        assertEquals(PlaybackAction.PLAY, PlaybackAction.from(Watched()))
        assertEquals(PlaybackAction.RESUME, PlaybackAction.from(Watched(position = 25), true))
        assertEquals(PlaybackAction.REWATCH, PlaybackAction.from(Watched(times = 1), true))
    }
}
