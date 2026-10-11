package net.seplis.tv.features.playback

import androidx.media3.common.FileTypes
import okhttp3.MediaType.Companion.toMediaTypeOrNull

object PlaybackSourceSelection {
    fun preferredIndex(candidates: List<PlayCandidate>, capabilities: PlaybackCapabilities,
        canPlayMediaType: (String) -> Boolean = ::supportsContainer): Int {
        val withinLimit = candidates.indices.filter { candidates[it].source.bitrate <= capabilities.maxBitrate }
        val compatible = withinLimit.filter {
            val source = candidates[it].source
            source.codec.lowercase() in capabilities.videoCodecs &&
                (source.hdr?.lowercase() != "hdr" || source.hdrType?.lowercase() in capabilities.hdrFormats)
        }
        return compatible.ifEmpty { withinLimit }.sortedWith(
            compareByDescending<Int> { width(candidates[it].source) }
                .thenByDescending { candidates[it].source.mediaType?.let(canPlayMediaType) == true }
                .thenBy { it }
        ).firstOrNull() ?: 0
    }

    @androidx.annotation.OptIn(androidx.media3.common.util.UnstableApi::class)
    internal fun supportsContainer(value: String): Boolean {
        val type = value.toMediaTypeOrNull() ?: return false
        // Video containers handled by Media3's default extractors.
        return when (FileTypes.inferFileTypeFromMimeType("${type.type}/${type.subtype}")) {
            FileTypes.MP4, FileTypes.MATROSKA, FileTypes.TS, FileTypes.PS, FileTypes.FLV, FileTypes.AVI -> true
            else -> false
        }
    }

    private fun width(source: PlaySource): Int = source.width.takeIf { it > 0 } ?: when (source.resolution.lowercase()) {
        "8k", "4320p" -> 7680
        "4k", "2160p" -> 3840
        "1440p" -> 2560
        "1080p" -> 1920
        "720p" -> 1280
        "480p" -> 854
        else -> 0
    }
}
