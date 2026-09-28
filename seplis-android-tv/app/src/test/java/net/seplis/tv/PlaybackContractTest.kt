package net.seplis.tv

import net.seplis.tv.features.library.Watched
import net.seplis.tv.features.playback.PlayCandidate
import net.seplis.tv.features.playback.PlayRequest
import net.seplis.tv.features.playback.PlaySource
import net.seplis.tv.features.playback.PlaybackAction
import net.seplis.tv.features.playback.PlaybackCapabilities
import net.seplis.tv.features.playback.PlaybackResolution
import net.seplis.tv.features.playback.PlaybackSourceSelection
import net.seplis.tv.features.playback.resolvePlayUrl
import org.junit.Assert.assertEquals
import org.junit.Test

class PlaybackContractTest {
    private fun candidate(width: Int, bitrate: Double, codec: String = "hevc", mediaType: String? = "video/mp4") = PlayCandidate(
        PlayRequest("id", "https://play.example.com/mount"),
        PlaySource(0, bitrate, "${width}p", codec, width, 1080, 3600.0,
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

    @Test fun playServerPathsStayUnderMountPoint() {
        assertEquals("https://play.example.com/mount/session/stream.m3u8",
            resolvePlayUrl("https://play.example.com/mount", "/session/stream.m3u8"))
        assertEquals("https://other.example.com/media.m3u8",
            resolvePlayUrl("https://play.example.com/mount", "https://other.example.com/media.m3u8"))
    }

    @Test fun mediaRequestUsesCodecPreferencesAndBitrateResolutionLimit() {
        val device = PlaybackCapabilities(listOf("hevc", "h264"), listOf("aac"), listOf("hdr10", "dovi"), 1_500_000)
        assertEquals("1920", device.query(false)["max_width"])
        assertEquals("1500000", device.query(false)["max_video_bitrate"])
        assertEquals("hevc", device.query(false)["transcode_video_codec"])
        assertEquals("aac", device.query(false)["transcode_audio_codec"])
        assertEquals("6", device.query(false)["max_audio_channels"])
        assertEquals("mp4,webm", device.query(false)["supported_video_containers"])
        assertEquals("3840", device.copy(maxBitrate = 200_000_000).query(false)["max_width"])
        val av1 = device.copy(videoCodecs = listOf("av1", "h264"), audioCodecs = listOf("flac", "opus"))
        assertEquals("av1", av1.query(false)["transcode_video_codec"])
        assertEquals("opus", av1.query(false)["transcode_audio_codec"])
    }

    @Test fun fallbackUsesH264ResolutionLimitAndDisablesHDR() {
        val device = PlaybackCapabilities(listOf("hevc", "h264"), listOf("aac"), listOf("hdr10", "dovi"), 1_500_000)
        assertEquals("h264", device.query(false, compatibilityFallback = true)["transcode_video_codec"])
        assertEquals("1280", device.query(false, compatibilityFallback = true)["max_width"])
        assertEquals("hdr10,dovi", device.query(false)["supported_hdr_formats"])
        assertEquals(null, device.query(false, compatibilityFallback = true)["supported_hdr_formats"])
    }

    @Test fun widthThresholdsUseTheNextTierAtTheBoundary() {
        val limits = mapOf(
            "h264" to listOf(1_000_000, 2_000_000, 5_000_000, 12_000_000),
            "hevc" to listOf(500_000, 1_000_000, 3_000_000, 8_000_000),
            "av1" to listOf(300_000, 800_000, 2_000_000, 6_000_000),
        )
        val widths = listOf(854, 1280, 1920, 2560, 3840)
        limits.forEach { (codec, thresholds) -> thresholds.forEachIndexed { index, bitrate ->
            assertEquals(widths[index], PlaybackResolution.recommendWidth(bitrate - 1, codec))
            assertEquals(widths[index + 1], PlaybackResolution.recommendWidth(bitrate, codec))
        } }
        assertEquals(1920, PlaybackResolution.recommendWidth(1_500_000, "h265"))
        assertEquals(3840, PlaybackResolution.recommendWidth(1_500_000, "unknown"))
    }

    @Test fun sourceLabelsIncludeHDRBitrateAndServer() {
        val original = candidate(1920, 20_000_000.0)
        assertEquals("1920p · HEVC · Dolby Vision · 20 Mbps · play.example.com",
            original.copy(source = original.source.copy(hdr = "HDR", hdrType = "DOVI")).label)
    }

    @Test fun playbackActionUsesSavedPositionAndWatchCount() {
        assertEquals(PlaybackAction.PLAY, PlaybackAction.from(Watched()))
        assertEquals(PlaybackAction.RESUME, PlaybackAction.from(Watched(position = 25), true))
        assertEquals(PlaybackAction.REWATCH, PlaybackAction.from(Watched(times = 1), true))
    }
}
