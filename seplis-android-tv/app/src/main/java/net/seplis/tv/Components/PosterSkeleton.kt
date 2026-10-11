package net.seplis.tv.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

@Composable
fun PosterSkeleton(width: Dp = LibraryStyle.posterWidth) {
    Box(Modifier.size(width, width * 1.5f).background(LibraryStyle.controlBackground, RoundedCornerShape(4.dp)))
}
