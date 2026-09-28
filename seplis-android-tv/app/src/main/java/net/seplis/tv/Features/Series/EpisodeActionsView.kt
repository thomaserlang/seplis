package net.seplis.tv.features.series

import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import net.seplis.tv.features.series.Episode
import net.seplis.tv.features.playback.PlaybackAction
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.TvButton

import net.seplis.tv.components.WatchedButton
@Composable
fun EpisodeActionsView(heading: String, episode: Episode, forceRewatch: Boolean = false,
    modifier: Modifier = Modifier, playFocusRequester: FocusRequester? = null, isUpdating: Boolean = false,
    onPlay: (Boolean) -> Unit, onWatched: (Boolean) -> Unit) {
    val action = if (forceRewatch) PlaybackAction.REWATCH else PlaybackAction.from(episode.watched, rewatchCompleted = true)
    Column(modifier, verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(heading, color = LibraryStyle.muted, fontSize = 10.sp, lineHeight = 13.sp, fontWeight = FontWeight.Medium)
        Column(Modifier.fillMaxWidth().border(0.5.dp, Color(0xFF242424), RoundedCornerShape(4.dp))
            .padding(start = 8.dp, end = 8.dp, top = 5.dp, bottom = 8.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                Text(episode.numberLabel, color = Color(0xFF8CBAE8), fontSize = 11.sp, lineHeight = 14.sp, fontWeight = FontWeight.SemiBold)
                episode.formattedAirDate()?.let { Text(it, color = LibraryStyle.muted, fontSize = 11.sp, lineHeight = 14.sp) }
            }
            Text(episode.title.orEmpty(), fontSize = 12.sp, lineHeight = 15.sp, maxLines = 1, overflow = TextOverflow.Ellipsis, fontWeight = FontWeight.Medium)
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                TvButton(action.label, { onPlay(action.fromBeginning) },
                    modifier = playFocusRequester?.let { Modifier.focusRequester(it) } ?: Modifier,
                    enabled = episode.canPlay, icon = action.icon)
                WatchedButton(episode.watched, { onWatched(true) }, { onWatched(false) }, episode.runtime,
                    enabled = !isUpdating)
            }
        }
    }
}
