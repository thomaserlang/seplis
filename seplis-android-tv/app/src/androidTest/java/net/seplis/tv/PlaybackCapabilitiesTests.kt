package net.seplis.tv

import androidx.test.platform.app.InstrumentationRegistry
import net.seplis.tv.features.playback.PlaybackCapabilities
import org.junit.Assert.*
import org.junit.Test

class PlaybackCapabilitiesTests {
    private val context get() = InstrumentationRegistry.getInstrumentation().targetContext

    @Test fun mediaTypeChecksCodecsNotJustTheContainer() {
        assertTrue(PlaybackCapabilities.canPlayMediaType(context, "video/mp4"))
        assertTrue(PlaybackCapabilities.canPlayMediaType(context,
            "video/mp4; codecs=\"avc1.42E01E,mp4a.40.2\""))
        assertFalse(PlaybackCapabilities.canPlayMediaType(context,
            "video/mp4; codecs=\"avc1.42E01E,unknown\""))
        assertFalse(PlaybackCapabilities.canPlayMediaType(context, "not a media type"))
    }

    @Test fun detectionKeepsBaselineCodecsAndHonorsHDRSetting() {
        val capabilities = PlaybackCapabilities.detect(context, 5_000_000, hdrEnabled = false)
        assertTrue("h264" in capabilities.videoCodecs)
        assertTrue("aac" in capabilities.audioCodecs)
        assertTrue("mp3" in capabilities.audioCodecs)
        assertTrue(capabilities.hdrFormats.isEmpty())
    }
}
