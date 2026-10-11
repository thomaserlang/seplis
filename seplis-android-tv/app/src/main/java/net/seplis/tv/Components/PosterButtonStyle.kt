package net.seplis.tv.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.border
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
internal fun Modifier.posterButtonStyle(focused: Boolean): Modifier {
    val scale by animateFloatAsState(if (focused) 1.06f else 1f,
        animationSpec = tween(150), label = "poster focus")
    return scale(scale).border(2.dp, if (focused) Color.White else Color.Transparent,
        RoundedCornerShape(4.dp))
}
