package net.seplis.tv.components

import androidx.compose.foundation.background
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

internal fun Modifier.navigationButtonStyle(focused: Boolean, selected: Boolean,
    enabled: Boolean, pressed: Boolean, selectedColor: Color): Modifier =
    alpha(if (!enabled) 0.4f else if (pressed) 0.8f else 1f)
        .clip(RoundedCornerShape(4.dp))
        .background(if (focused) Color.White else if (selected) selectedColor else Color.Transparent)

internal fun navigationButtonContentColor(focused: Boolean): Color =
    if (focused) Color.Black else Color.White
