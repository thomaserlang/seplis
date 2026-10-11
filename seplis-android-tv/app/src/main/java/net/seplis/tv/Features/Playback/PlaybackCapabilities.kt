package net.seplis.tv.features.playback

import android.content.Context
import android.hardware.display.DisplayManager
import android.os.Build
import android.view.Display
import androidx.media3.common.C
import androidx.media3.common.ColorInfo
import androidx.media3.common.Format
import androidx.media3.common.MimeTypes
import androidx.media3.exoplayer.mediacodec.MediaCodecUtil
import okhttp3.MediaType.Companion.toMediaTypeOrNull

data class PlaybackCapabilities(val videoCodecs: List<String>, val audioCodecs: List<String>,
    val hdrFormats: List<String>, val maxBitrate: Int, val maxAudioChannels: Int = 6) {
    @androidx.annotation.OptIn(androidx.media3.common.util.UnstableApi::class)
    companion object {
        fun detect(context: Context, maxBitrate: Int, hdrEnabled: Boolean): PlaybackCapabilities {
            // Keep the probes and preference order aligned with seplis-ui's video.utils.ts.
            val video = buildList {
                if (supports(context, format("hvc1")) || supports(context, format("hev1.1.6.L93.90"))) add("hevc")
                val av1 = format("av01.0.08M.08").buildUpon().setWidth(1920).setHeight(1080)
                    .setFrameRate(24f).setAverageBitrate(8_000_000).build()
                if (supports(context, av1)) add("av1")
                if (supports(context, format("avc1.42E01E"))) add("h264")
            }
            val audio = linkedMapOf(
                "aac" to listOf(MimeTypes.AUDIO_AAC), "eac3" to listOf(MimeTypes.AUDIO_E_AC3),
                "ac3" to listOf(MimeTypes.AUDIO_AC3), "ac4" to listOf(MimeTypes.AUDIO_AC4),
                "opus" to listOf(MimeTypes.AUDIO_OPUS), "flac" to listOf(MimeTypes.AUDIO_FLAC),
                "dts" to listOf(MimeTypes.AUDIO_DTS, MimeTypes.AUDIO_DTS_EXPRESS, MimeTypes.AUDIO_DTS_UHD_P2),
                "mp3" to listOf(MimeTypes.AUDIO_MPEG),
            ).filterValues { types -> types.any {
                supports(context, Format.Builder().setSampleMimeType(it).build())
            } }.keys.toList()
            val display = context.getSystemService(DisplayManager::class.java)?.getDisplay(Display.DEFAULT_DISPLAY)
            val hdrTypes = if (hdrEnabled && display != null) supportedHdrTypes(display) else emptySet()
            fun supportsHDR(type: Int, codec: String, transfer: Int): Boolean {
                if (type !in hdrTypes) return false
                val probe = format(codec).buildUpon().setWidth(3840).setHeight(2160)
                    .setFrameRate(30f).setAverageBitrate(20_000_000)
                    .setColorInfo(ColorInfo.Builder().setColorSpace(C.COLOR_SPACE_BT2020)
                        .setColorRange(C.COLOR_RANGE_LIMITED).setColorTransfer(transfer).build()).build()
                return supports(context, probe)
            }
            val hdr = buildList {
                if (supportsHDR(Display.HdrCapabilities.HDR_TYPE_DOLBY_VISION, "dvh1.05.07", C.COLOR_TRANSFER_ST2084)) add("dovi")
                if (supportsHDR(Display.HdrCapabilities.HDR_TYPE_HDR10, "hev1.2.4.L153.B0", C.COLOR_TRANSFER_ST2084)) add("hdr10")
                if (supportsHDR(Display.HdrCapabilities.HDR_TYPE_HLG, "hev1.2.4.L153.B0", C.COLOR_TRANSFER_HLG)) add("hlg")
            }
            return PlaybackCapabilities(video, audio, hdr, maxBitrate)
        }

        fun canPlayMediaType(context: Context, value: String): Boolean {
            if (!PlaybackSourceSelection.supportsContainer(value)) return false
            val codecs = value.toMediaTypeOrNull()?.parameter("codecs") ?: return true
            return codecs.split(',').all { supports(context, format(it.trim())) }
        }

        private fun format(codec: String): Format = Format.Builder()
            .setSampleMimeType(MimeTypes.getMediaMimeType(codec)).setCodecs(codec).build()

        private fun supports(context: Context, format: Format): Boolean = runCatching {
            val mime = format.sampleMimeType ?: return false
            MediaCodecUtil.getDecoderInfos(mime, false, false).any { it.isFormatSupported(context, format) }
        }.getOrDefault(false)

        private fun supportedHdrTypes(display: Display): Set<Int> =
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
                display.mode.supportedHdrTypes.toSet()
            } else {
                // Android 11-13 have no mode-specific HDR API.
                @Suppress("DEPRECATION")
                display.hdrCapabilities?.supportedHdrTypes?.toSet() ?: emptySet()
            }
    }

    fun query(forceTranscode: Boolean, compatibilityFallback: Boolean = false) = buildMap {
        val transcodeCodec = if (compatibilityFallback) "h264" else videoCodecs.firstOrNull() ?: "h264"
        val transcodeAudio = if (compatibilityFallback) "aac" else
            listOf("aac", "opus", "flac", "mp3").firstOrNull { it in audioCodecs } ?: "aac"
        put("supported_video_codecs", videoCodecs.joinToString(","))
        put("supported_audio_codecs", audioCodecs.joinToString(","))
        put("supported_video_containers", "mp4,webm")
        put("transcode_video_codec", transcodeCodec)
        put("transcode_audio_codec", transcodeAudio)
        put("max_audio_channels", maxAudioChannels.toString())
        put("max_video_bitrate", maxBitrate.toString())
        put("max_width", PlaybackResolution.recommendWidth(maxBitrate, transcodeCodec).toString())
        put("force_transcode", forceTranscode.toString())
        put("format", "hls")
        put("start_time", "0")
        put("hls_include_all_subtitles", "true")
        if (!compatibilityFallback && hdrFormats.isNotEmpty()) put("supported_hdr_formats", hdrFormats.joinToString(","))
    }
}
