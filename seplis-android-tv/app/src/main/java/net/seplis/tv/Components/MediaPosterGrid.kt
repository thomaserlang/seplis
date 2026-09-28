package net.seplis.tv.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.lazy.grid.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.focusRestorer
import androidx.compose.ui.unit.dp
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.Poster

data class MediaPosterItem(val reference: MediaReference, val title: String, val poster: Poster?) {
    val key get() = "${reference.kind}-${reference.id}"
}

@Composable
fun MediaPosterGrid(items: List<MediaPosterItem>, isLoading: Boolean, state: LazyGridState,
    refresh: Int, restoreKey: String?, onRestored: () -> Unit,
    onFocus: (Int, MediaPosterItem) -> Unit, onUp: () -> Unit,
    onOpen: (MediaReference) -> Unit, footer: (@Composable () -> Unit)? = null,
    onApproachEnd: () -> Unit = {}) {
    LazyVerticalGrid(GridCells.Adaptive(LibraryStyle.posterWidth), Modifier.fillMaxSize().focusRestorer(), state = state,
        contentPadding = PaddingValues(horizontal = LibraryStyle.horizontalInset, vertical = 5.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        itemsIndexed(items, key = { _, item -> item.key }) { index, item ->
            LaunchedEffect(item.key, items.size) {
                if (index >= items.size - 16) onApproachEnd()
            }
            val focus = remember(item.key) { FocusRequester() }
            LaunchedEffect(item.key, restoreKey, refresh) {
                if (restoreKey == item.key) {
                    onRestored()
                    focus.requestFocus()
                }
            }
            PosterView(item.title, item.poster, { onOpen(item.reference) }, Modifier.focusRequester(focus),
                onFocus = { onFocus(index, item) }, onUp = {
                    val firstRow = state.layoutInfo.visibleItemsInfo.firstOrNull { it.index == index }?.row == 0
                    if (firstRow) onUp()
                    firstRow
                })
        }
        if (isLoading) items(18) { PosterSkeleton() }
        if (footer != null) item(span = { GridItemSpan(maxLineSpan) }) { footer() }
    }
}
