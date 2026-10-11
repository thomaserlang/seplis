package net.seplis.tv.features.playback

import androidx.media3.common.C
import androidx.media3.common.Player
import androidx.media3.common.TrackSelectionOverride

object PlayerSubtitleSelection {
    fun apply(player: Player, stream: PlayStream?): Boolean {
        val parameters = player.trackSelectionParameters.buildUpon().clearOverridesOfType(C.TRACK_TYPE_TEXT)
            .setTrackTypeDisabled(C.TRACK_TYPE_TEXT, stream == null)
        if (stream == null) {
            player.trackSelectionParameters = parameters.build()
            return true
        }
        val tracks = player.currentTracks.groups.filter { it.type == C.TRACK_TYPE_TEXT }.flatMap { group ->
            (0 until group.length).map { index -> group to index }
        }
        val candidates = tracks.withIndex().filter { (_, track) ->
            PlaybackLanguages.matches(track.first.getTrackFormat(track.second).language.orEmpty(), stream.language)
        }
        val selected = candidates.minByOrNull { kotlin.math.abs(it.index - (stream.groupIndex ?: 0)) }?.value ?: return false
        player.trackSelectionParameters = parameters.setOverrideForType(
            TrackSelectionOverride(selected.first.mediaTrackGroup, selected.second)).build()
        return true
    }
}
