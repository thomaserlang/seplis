package net.seplis.tv.components

import net.seplis.tv.features.library.Watched

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.CheckBox
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material.icons.filled.Replay
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.tv.material3.Text
import net.seplis.tv.components.Palette
import net.seplis.tv.components.TvButton

@Composable
fun WatchedButton(watched: Watched, onIncrement: () -> Unit, onDecrement: () -> Unit,
    durationMinutes: Int? = null, enabled: Boolean = true, modifier: Modifier = Modifier) {
    var open by remember { mutableStateOf(false) }
    var focused by remember { mutableStateOf(false) }
    val interactionSource = remember { MutableInteractionSource() }
    val pressed by interactionSource.collectIsPressedAsState()
    val shape = RoundedCornerShape(4.dp)
    val progress = when {
        watched.position <= 0 -> 0f
        durationMinutes == null || durationMinutes <= 0 -> 0.5f
        else -> (watched.position.toFloat() / (durationMinutes * 60)).coerceIn(0.15f, 1f)
    }

    Row(modifier.height(31.dp).libraryButtonStyle(focused, enabled, pressed)
        .semantics(mergeDescendants = true) {
            contentDescription = "Watched"
            stateDescription = "${watched.times} times" + if (watched.position > 0) ", in progress" else ""
        }
        .onFocusChanged { focused = it.isFocused }
        .clickable(enabled = enabled, role = Role.Button, interactionSource = interactionSource,
            indication = null) { if (watched.times == 0 && watched.position == 0) onIncrement() else open = true },
        verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.fillMaxHeight()
            .background(if (watched.times > 0) Color(0xFF2E5C82) else Palette.surface)
            .drawWithContent {
                drawContent()
                if (progress > 0f) {
                    val strip = 2.dp.toPx()
                    drawRect(Color(0xFF6BABD6), Offset(0f, size.height - strip),
                        Size(size.width * progress, strip))
                }
            }
            .padding(horizontal = 8.dp), contentAlignment = Alignment.Center) {
            Row(horizontalArrangement = Arrangement.spacedBy(5.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(if (watched.times > 0) Icons.Filled.CheckBox else Icons.Filled.Check,
                    contentDescription = null, tint = Color.White, modifier = Modifier.size(12.dp))
                Text("Watched", color = Color.White, fontSize = 12.sp, lineHeight = 15.sp,
                    fontWeight = FontWeight.Medium)
            }
        }
        Box(Modifier.width(0.5.dp).fillMaxHeight().background(Color.White.copy(alpha = 0.15f)))
        Box(Modifier.width(26.dp).fillMaxHeight().background(Palette.surface),
            contentAlignment = Alignment.Center) {
            Text(watched.times.toString(), color = Color.White, fontSize = 12.sp, lineHeight = 15.sp,
                fontWeight = FontWeight.Medium)
        }
    }

    if (open) Dialog(onDismissRequest = { open = false }) {
        Column(Modifier.width(220.dp).background(Palette.surface, shape).padding(10.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text("Watched ${watched.times} times", fontSize = 14.sp, modifier = Modifier.padding(8.dp))
            TvButton(if (watched.position > 0 || watched.times == 0) "Mark as watched" else "Add another watch",
                { onIncrement(); open = false }, Modifier.fillMaxWidth(),
                icon = if (watched.position > 0) Icons.Filled.Check else Icons.Filled.Add)
            TvButton(if (watched.position > 0) "Reset watched position" else "Remove last watch",
                { onDecrement(); open = false }, Modifier.fillMaxWidth(),
                icon = if (watched.position > 0) Icons.Filled.Replay else Icons.Filled.Remove)
            if (watched.position > 0) {
                Text("Resetting clears the saved playback position without removing completed watches.",
                    color = Palette.muted, fontSize = 10.sp, modifier = Modifier.padding(horizontal = 8.dp))
            }
            TvButton("Cancel", { open = false }, Modifier.fillMaxWidth())
        }
    }
}
