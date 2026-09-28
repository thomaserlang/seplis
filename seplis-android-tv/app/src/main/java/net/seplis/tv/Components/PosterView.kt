package net.seplis.tv.components
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Movie
import androidx.compose.material3.Icon
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.type
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import coil3.compose.AsyncImage
import net.seplis.tv.features.library.Poster

@Composable
fun PosterTile(
    title: String, poster: Poster?, onClick: () -> Unit, modifier: Modifier = Modifier,
    width: Dp = 92.dp, height: Dp = 138.dp, onFocus: (() -> Unit)? = null,
    onUp: (() -> Boolean)? = null,
    enabled: Boolean = true,
) {
    var focused by remember { mutableStateOf(false) }
    var failed by remember(poster) { mutableStateOf(false) }
    val scale by animateFloatAsState(if (focused) 1.06f else 1f,
        animationSpec = tween(150), label = "poster focus")
    val shape = RoundedCornerShape(4.dp)
    // Focus and bring-into-view use fixed bounds; only the visual content zooms.
    Box(modifier.width(width).height(height)
        .semantics { contentDescription = title }
        .onFocusChanged { focused = it.isFocused; if (it.isFocused) onFocus?.invoke() }
        .onPreviewKeyEvent {
            if (focused && onUp != null && it.type == KeyEventType.KeyDown && it.key == Key.DirectionUp) {
                onUp()
            } else false
        }
        .clickable(enabled = enabled, onClick = onClick)) {
        Box(Modifier.matchParentSize().scale(scale).clip(shape).background(Palette.surface)) {
            if (poster != null && !failed) {
                AsyncImage(model = poster.thumbnail, contentDescription = null,
                    modifier = Modifier.matchParentSize(), contentScale = ContentScale.Crop, onError = { failed = true })
            } else {
                Column(Modifier.align(Alignment.Center).padding(8.dp), horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Icon(Icons.Default.Movie, null, tint = Palette.muted, modifier = Modifier.size(18.dp))
                    Text(title, color = Palette.muted, fontSize = 11.sp, maxLines = 3,
                        textAlign = TextAlign.Center, overflow = TextOverflow.Ellipsis)
                }
            }
            if (focused) Box(Modifier.matchParentSize().border(2.dp, Color.White, shape))
        }
    }
}
