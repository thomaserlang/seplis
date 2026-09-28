package net.seplis.tv

import net.seplis.tv.features.playback.PlaybackCapabilities
import net.seplis.tv.features.playback.PlaybackResolution
import org.junit.Assert.assertEquals
import org.junit.Test

class PlaybackCapabilitiesTests {
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
}
