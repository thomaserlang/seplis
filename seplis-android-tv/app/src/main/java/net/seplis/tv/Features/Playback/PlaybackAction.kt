package net.seplis.tv.features.playback
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Replay
import androidx.compose.ui.graphics.vector.ImageVector
import net.seplis.tv.features.library.Watched

enum class PlaybackAction(val label: String, val fromBeginning: Boolean) {
    PLAY("Play", true), RESUME("Resume", false), REWATCH("Rewatch", true);

    val icon: ImageVector get() = if (this == REWATCH) Icons.Filled.Replay else Icons.Filled.PlayArrow

    companion object {
        fun from(watched: Watched, rewatchCompleted: Boolean = false): PlaybackAction = when {
            watched.position > 0 -> RESUME
            rewatchCompleted && watched.times > 0 -> REWATCH
            else -> PLAY
        }
    }
}
