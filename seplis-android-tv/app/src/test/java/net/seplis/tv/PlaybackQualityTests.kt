package net.seplis.tv

import net.seplis.tv.features.playback.PlaybackQuality
import net.seplis.tv.features.playback.PlaybackLanguages
import org.junit.Assert.*
import org.junit.Test

class PlaybackQualityTests {
    @Test fun qualityLabelsPreserveFractionalAndLowBitrates() {
        assertEquals("Max (25 Mbps)", PlaybackQuality.label(PlaybackQuality.maximum, 25_000_000.0))
        assertEquals("1.5 Mbps", PlaybackQuality.label(1_500_000))
        assertEquals("720 kbps", PlaybackQuality.label(720_000))
        assertEquals("420 kbps", PlaybackQuality.label(420_000))
    }

    @Test fun availableQualityKeepsSavedChoiceAndOmitsHigherThanSource() {
        val options = PlaybackQuality.available(8_000_000.0, 20_000_000)
        assertTrue(PlaybackQuality.maximum in options)
        assertTrue(20_000_000 in options)
        assertTrue(6_000_000 in options)
        assertFalse(40_000_000 in options)
        assertFalse(8_000_000 in options)
    }

    @Test fun languageMatchingAcceptsTwoAndThreeLetterCodesAndRegions() {
        assertTrue(PlaybackLanguages.matches("en-US", "eng"))
        assertTrue(PlaybackLanguages.matches("ja", "jpn"))
        assertFalse(PlaybackLanguages.matches("eng", "dan"))
    }
}
