package net.seplis.tv.features.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRestorer
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import kotlinx.coroutines.launch
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.components.MessagePanel
import net.seplis.tv.components.Palette

@Composable
fun HomeView(store: HomeStore, refresh: Int, contentEntry: Int,
    onMenuFocus: () -> Unit, onOpen: (MediaReference) -> Unit, isActive: Boolean = true,
    autoFocusOnLoad: Boolean = true) {
    val listState = rememberLazyListState()
    val firstFocus = remember { FocusRequester() }
    LaunchedEffect(store, refresh, isActive) {
        if (isActive) {
            HomeShelf.entries.forEach { shelf -> launch { store.shelf(shelf).load() } }
        }
    }
    val firstShelf = HomeShelf.entries.firstOrNull {
        val shelf = store.shelf(it)
        (!shelf.loaded && shelf.error == null) || shelf.items.isNotEmpty()
    }
    var handledEntry by remember { mutableIntStateOf(0) }
    LaunchedEffect(contentEntry, firstShelf) {
        if (contentEntry > 0 && contentEntry != handledEntry && firstShelf != null) {
            handledEntry = contentEntry
            listState.scrollToItem(HomeShelf.entries.indexOf(firstShelf))
        }
    }
    LazyColumn(modifier = Modifier.focusRestorer(), state = listState, contentPadding = PaddingValues(bottom = 20.dp),
        verticalArrangement = Arrangement.spacedBy(3.dp)) {
        items(HomeShelf.entries, key = HomeShelf::name) { shelf ->
            val state = store.shelf(shelf)
            val scope = rememberCoroutineScope()
            if (!state.loaded || state.items.isNotEmpty() || state.error != null) {
                Column {
                    Text(shelf.title, Modifier.padding(start = 16.dp),
                        fontSize = 11.sp, color = Palette.muted)
                    if (state.error != null && state.items.isEmpty()) {
                        MessagePanel(state.error ?: "Could not load", retry = { scope.launch { state.load() } })
                    } else {
                        ShelfPosters(shelf, state, store, refresh,
                            if (shelf == firstShelf) firstFocus else null,
                            if (shelf == firstShelf) contentEntry else 0,
                            onUp = if (shelf == firstShelf) onMenuFocus else null, onOpen,
                            autoFocusOnLoad = autoFocusOnLoad && isActive)
                    }
                }
            }
        }
    }
}
