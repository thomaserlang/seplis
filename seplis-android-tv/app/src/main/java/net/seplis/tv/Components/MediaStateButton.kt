package net.seplis.tv.components

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector

@Composable
fun MediaStateButton(title: String, symbol: ImageVector, isActive: Boolean, color: Color,
    action: () -> Unit, modifier: Modifier = Modifier, enabled: Boolean = true) {
    TvButton(title, action, modifier, selected = isActive, color = color, enabled = enabled,
        icon = symbol, accessibilityValue = if (isActive) "On" else "Off")
}
