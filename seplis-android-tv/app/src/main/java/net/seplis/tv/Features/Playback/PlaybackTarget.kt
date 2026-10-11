package net.seplis.tv.features.playback

import net.seplis.tv.features.series.Episode
import net.seplis.tv.features.library.MediaReference

data class PlaybackTarget(
    val reference: MediaReference, val title: String, val episode: Episode? = null, val fromBeginning: Boolean = false,
) {
    val path: String get() = episode?.let { "${reference.path}/episodes/${it.number}" } ?: reference.path
}
