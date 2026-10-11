package net.seplis.tv.features.series

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.TvButton
import net.seplis.tv.components.WatchedButton
import net.seplis.tv.features.series.Episode
import net.seplis.tv.features.playback.PlaybackAction

@Composable
fun SeasonEpisodeRow(episode: Episode, isUpdating: Boolean, onPlay: (Boolean) -> Unit,
    onIncrement: () -> Unit, onDecrement: () -> Unit) {
    val action = PlaybackAction.from(episode.watched, rewatchCompleted = true)
    val shape = RoundedCornerShape(4.dp)
    Column(Modifier.fillMaxWidth().background(Color(0xFF0B0B0B), shape)
        .border(0.5.dp, Color(0xFF292929), shape).padding(8.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) {
            Text(episode.numberLabel, color = Color(0xFF8AB7E0), fontSize = 11.sp,
                lineHeight = 14.sp, fontWeight = FontWeight.SemiBold)
            episode.formattedAirDate()?.let { Text(it, color = LibraryStyle.muted, fontSize = 9.5.sp, lineHeight = 12.sp) }
            Spacer(Modifier.weight(1f))
            episode.runtime?.let { Text("${it} min", color = LibraryStyle.muted, fontSize = 9.5.sp, lineHeight = 12.sp) }
        }
        Text(episode.title ?: "Episode ${episode.episode ?: episode.number}", fontSize = 12.5.sp, lineHeight = 15.sp,
            fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis)
        episode.plot?.takeIf { it.isNotBlank() }?.let {
            Text(it, color = LibraryStyle.muted, fontSize = 10.sp, lineHeight = 13.sp, maxLines = 2,
                overflow = TextOverflow.Ellipsis)
        }
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            TvButton(action.label, { onPlay(action.fromBeginning) }, enabled = episode.canPlay, icon = action.icon,
                accessibilityLabel = "${action.label} ${episode.label}")
            WatchedButton(episode.watched, onIncrement, onDecrement, episode.runtime, enabled = !isUpdating)
        }
    }
}
