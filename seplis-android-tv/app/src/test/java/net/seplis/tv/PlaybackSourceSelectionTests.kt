package net.seplis.tv

import net.seplis.tv.features.playback.PlayCandidate
import net.seplis.tv.features.playback.PlayRequest
import net.seplis.tv.features.playback.PlaySource
import net.seplis.tv.features.playback.PlaybackCapabilities
import net.seplis.tv.features.playback.PlaybackSourceSelection
import org.junit.Assert.assertEquals
import org.junit.Test

class PlaybackSourceSelectionTests {
    private fun candidate(width: Int, bitrate: Double, codec: String = "hevc", mediaType: String? = "video/mp4") = PlayCandidate(
        PlayRequest("id", "https://play.example.com/mount"),
        PlaySource(0, bitrate, "1080p", codec, width, 1080, 3600.0,
            emptyList(), emptyList(), null, null, "mkv", mediaType),
    )

    @Test fun sourceSelectionPrefersResolutionWithinBitrateLimit() {
        val candidates = listOf(candidate(1920, 4_000_000.0), candidate(3840, 20_000_000.0))
        val device = PlaybackCapabilities(listOf("hevc", "h264"), listOf("aac"), emptyList(), 25_000_000)
        assertEquals(1, PlaybackSourceSelection.preferredIndex(candidates, device))
        assertEquals(0, PlaybackSourceSelection.preferredIndex(candidates, device.copy(maxBitrate = 10_000_000)))
        assertEquals(1, PlaybackSourceSelection.preferredIndex(listOf(candidate(1920, 4_000_000.0, mediaType = null),
            candidate(3840, 20_000_000.0)), device))
        assertEquals(1, PlaybackSourceSelection.preferredIndex(listOf(candidate(1920, 4_000_000.0),
            candidate(3840, 20_000_000.0, mediaType = null)), device))
    }

    @Test fun sourceSelectionPrefersCompatibleCodec() {
        val candidates = listOf(candidate(3840, 20_000_000.0, "av1"), candidate(1920, 8_000_000.0))
        val device = PlaybackCapabilities(listOf("hevc", "h264"), listOf("aac"), emptyList(), 25_000_000)
        assertEquals(1, PlaybackSourceSelection.preferredIndex(candidates, device))
    }

    @Test fun sourceLabelsIncludeHDRBitrateAndServer() {
        val original = candidate(1920, 20_000_000.0)
        assertEquals("1080p · HEVC · Dolby Vision · 20 Mbps · play.example.com",
            original.copy(source = original.source.copy(hdr = "HDR", hdrType = "DOVI")).label)
    }
}
