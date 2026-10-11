package net.seplis.tv.features.library

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.BringIntoViewSpec
import androidx.compose.foundation.gestures.LocalBringIntoViewSpec
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.focusRestorer
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.Dp
import net.seplis.tv.components.LibraryStyle

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun MediaDetailLayout(poster: Poster?, headerSpacing: Dp = 12.dp,
    scrollContent: Boolean = true,
    header: @Composable () -> Unit, content: @Composable () -> Unit) {
    val scroll = rememberScrollState()
    val minimumScroll = remember { object : BringIntoViewSpec {} }
    BoxWithConstraints(Modifier.fillMaxSize().background(LibraryStyle.background)) {
        val artworkWidth = maxHeight * 2 / 3
        val contentWidth = maxWidth - artworkWidth
        val leadingInset = maxOf(32.dp, maxWidth * 0.04f)
        Row(Modifier.fillMaxSize()) {
            Column(Modifier.width(contentWidth).fillMaxHeight()
                .padding(start = leadingInset, end = 24.dp, top = 28.dp)) {
                header()
                Spacer(Modifier.height(headerSpacing))
                CompositionLocalProvider(LocalBringIntoViewSpec provides minimumScroll) {
                    if (scrollContent) {
                        Column(Modifier.fillMaxWidth().focusRestorer().verticalScroll(scroll).padding(bottom = 28.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)) { content() }
                    } else {
                        Box(Modifier.fillMaxWidth().weight(1f)) { content() }
                    }
                }
            }
            MediaDetailArtwork(poster, Modifier.width(artworkWidth).fillMaxHeight())
        }
    }
}
