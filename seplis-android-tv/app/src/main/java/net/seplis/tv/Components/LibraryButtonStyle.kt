package net.seplis.tv.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.type
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import androidx.compose.material3.Icon

internal fun Modifier.libraryButtonStyle(focused: Boolean, enabled: Boolean, pressed: Boolean,
    background: Color = Color.Transparent): Modifier {
    val shape = RoundedCornerShape(4.dp)
    return alpha(if (!enabled) 0.4f else if (pressed) 0.75f else 1f)
        .clip(shape)
        .background(background)
        .border(1.5.dp, if (focused) Color.White else Color.Transparent, shape)
}

@Composable
fun TvButton(
    label: String, onClick: () -> Unit, modifier: Modifier = Modifier,
    selected: Boolean? = null, enabled: Boolean = true, color: Color = Palette.blue,
    flat: Boolean = false, icon: ImageVector? = null, iconOnly: Boolean = false,
    onFocusChange: ((Boolean) -> Unit)? = null,
    onDown: (() -> Unit)? = null,
    onUp: (() -> Unit)? = null,
    subtitle: String? = null,
    trailingIcon: ImageVector? = null,
    trailingText: String? = null,
    alignStart: Boolean = false,
    accessibilityLabel: String? = null,
    accessibilityValue: String? = null,
) {
    var focused by remember { mutableStateOf(false) }
    val interactionSource = remember { MutableInteractionSource() }
    val pressed by interactionSource.collectIsPressedAsState()
    Box(modifier
        .libraryButtonStyle(focused && !flat, enabled, pressed,
            if (focused && flat) Color.White else if (selected == true) color else if (flat) Color.Transparent else Palette.surface)
        .semantics {
            if (iconOnly || accessibilityLabel != null) contentDescription = accessibilityLabel ?: label
            selected?.let { this.selected = it }
            accessibilityValue?.let { stateDescription = it }
        }
        .onFocusChanged {
            if (focused != it.isFocused) {
                focused = it.isFocused
                onFocusChange?.invoke(it.isFocused)
            }
        }
        .onPreviewKeyEvent {
            if (!focused || it.type != KeyEventType.KeyDown) false
            else when (it.key) {
                Key.DirectionDown -> onDown?.let { action -> action(); true } ?: false
                Key.DirectionUp -> onUp?.let { action -> action(); true } ?: false
                else -> false
            }
        }
        .clickable(enabled = enabled, role = Role.Button, interactionSource = interactionSource,
            indication = null, onClick = onClick)
        .height(if (subtitle != null) 49.dp else if (flat) 28.dp else 31.dp)
        .padding(horizontal = 12.dp),
        contentAlignment = if (subtitle == null && !alignStart) Alignment.Center else Alignment.CenterStart) {
        val contentColor = if (focused && flat) Color.Black else Color.White
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(7.dp)) {
            icon?.let { Icon(it, contentDescription = null, tint = contentColor, modifier = Modifier.size(14.dp)) }
            if (!iconOnly) Column(if (trailingIcon != null || trailingText != null) Modifier.weight(1f) else Modifier) {
                Text(label, fontSize = 13.sp, lineHeight = 16.sp, fontWeight = FontWeight.Medium,
                    color = contentColor, maxLines = 1, overflow = TextOverflow.Ellipsis)
                subtitle?.let { Text(it, fontSize = 10.sp, lineHeight = 13.sp, color = Palette.muted, maxLines = 1) }
            }
            trailingIcon?.let { Icon(it, null, tint = contentColor, modifier = Modifier.size(14.dp)) }
            trailingText?.let { Text(it, fontSize = 9.sp, color = contentColor, maxLines = 1) }
        }
    }
}
