package net.seplis.tv.features.home
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.withFrameNanos
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRestorer
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.components.Palette
import net.seplis.tv.components.PosterTile

@Composable
internal fun ShelfPosters(shelf: HomeShelf, state: HomeShelfModel, store: HomeStore, refresh: Int,
    firstFocus: FocusRequester?, contentEntry: Int, onUp: (() -> Unit)?, onOpen: (MediaReference) -> Unit,
    autoFocusOnLoad: Boolean) {
    val scope = rememberCoroutineScope()
    val rowState = rememberLazyListState()
    LaunchedEffect(contentEntry, state.items.isNotEmpty()) {
        if (contentEntry > 0 && state.items.isNotEmpty() && firstFocus != null) {
            rowState.scrollToItem(0)
            withFrameNanos { }
            firstFocus.requestFocus()
        }
    }
    LazyRow(modifier = Modifier.focusRestorer(), state = rowState, contentPadding = PaddingValues(horizontal = 16.dp, vertical = 5.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        if (state.items.isEmpty()) {
            items(7) {
                net.seplis.tv.components.PosterSkeleton()
            }
        } else {
            itemsIndexed(state.items, key = { _, item -> item.key }) { index, item ->
                LaunchedEffect(item.key, state.items.size) {
                    if (index >= state.items.size - 8 && state.cursor != null && state.error == null) {
                        scope.launch { state.load(more = true) }
                    }
                }
                val localFocus = remember(item.key) { FocusRequester() }
                val focus = if (index == 0 && firstFocus != null) firstFocus else localFocus
                LaunchedEffect(item.key, refresh, firstFocus, autoFocusOnLoad) {
                    if (store.restoreFocusPending && store.focusedShelf == shelf && store.focusedKey == item.key) {
                        store.restoreFocusPending = false
                        focus.requestFocus()
                    } else if (autoFocusOnLoad && !store.focusClaimed && index == 0 && firstFocus != null) {
                        store.focusClaimed = true
                        focus.requestFocus()
                    }
                }
                PosterTile(item.media.title, item.media.poster, { onOpen(item.reference) },
                    modifier = Modifier.focusRequester(focus),
                    onFocus = {
                        store.focusedShelf = shelf
                        store.focusedKey = item.key
                        if (index >= state.items.size - 8 && state.cursor != null && state.error == null) {
                            scope.launch { state.load(more = true) }
                        }
                    }, onUp = onUp?.let { action -> { action(); true } })
            }
            if (state.isLoadingMore) item { net.seplis.tv.components.PosterSkeleton() }
            state.error?.let { message -> item {
                net.seplis.tv.components.MessagePanel(message, { scope.launch { state.load(more = true) } }, Modifier.width(220.dp))
            } }
        }
    }
}
