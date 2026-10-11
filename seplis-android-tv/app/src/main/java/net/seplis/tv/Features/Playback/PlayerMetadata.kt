package net.seplis.tv.features.playback

import androidx.media3.common.MediaMetadata

object PlayerMetadata {
    fun items(title: String, subtitle: String?): MediaMetadata =
        MediaMetadata.Builder().setTitle(title).setSubtitle(subtitle).build()
}
