package net.seplis.tv.features.library

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import coil3.compose.AsyncImage
import net.seplis.tv.components.Palette

@Composable
fun MediaDetailArtwork(poster: Poster?, modifier: Modifier = Modifier) {
    Box(modifier.background(Palette.surface)) {
        AsyncImage(model = poster?.url, contentDescription = null,
            modifier = Modifier.matchParentSize(), contentScale = ContentScale.Crop)
        Box(Modifier.fillMaxWidth(0.14f).fillMaxHeight()
            .background(Brush.horizontalGradient(listOf(Palette.background, Color.Transparent))))
    }
}
