package net.seplis.tv.features.library

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.lazy.grid.rememberLazyGridState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.withFrameNanos
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import kotlinx.coroutines.launch
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.components.MessagePanel
import net.seplis.tv.components.MediaPosterGrid
import net.seplis.tv.components.MediaPosterItem

@Composable
fun CatalogView(kind: MediaKind, store: CatalogModel, refresh: Int, contentEntry: Int,
    onMenuFocus: () -> Unit, onOpen: (MediaReference) -> Unit) {
    val scope = rememberCoroutineScope()
    val firstFilter = remember { FocusRequester() }
    val gridState = androidx.compose.runtime.key(store.filters) { rememberLazyGridState() }
    LaunchedEffect(contentEntry) {
        if (contentEntry > 0) { withFrameNanos { }; firstFilter.requestFocus() }
    }
    var filtersOpen by remember { mutableStateOf(false) }
    LaunchedEffect(store.filters) { store.ensureLoaded(0) }
    fun loadMore() {
        if (store.cursor != null && store.error == null) scope.launch { store.load(more = true) }
    }
    Column(Modifier.fillMaxSize()) {
        CatalogQuickFilters(kind, store.filters, firstFilter, { store.filters = it }, onMenuFocus) { filtersOpen = true }
        if (store.error != null && store.items.isEmpty()) {
            MessagePanel(store.error ?: "Could not load", { scope.launch { store.load() } })
        } else {
            val empty = store.hasLoaded && !store.loading && store.items.isEmpty() && store.error == null
            MediaPosterGrid(store.items.map { MediaPosterItem(MediaReference(kind, it.id), it.title, it.poster) },
                isLoading = store.loading || !store.hasLoaded && store.error == null, state = gridState,
                refresh = refresh, restoreKey = store.focusedID?.takeIf { store.restoreFocusPending }?.let { "$kind-$it" },
                onRestored = { store.restoreFocusPending = false }, onFocus = { index, item ->
                    store.focusedID = item.reference.id
                    if (index >= store.items.size - 16) loadMore()
                }, onUp = { firstFilter.requestFocus() }, onOpen = onOpen,
                footer = if (empty || store.error != null) {{
                    if (empty) MessagePanel("No titles found")
                    else MessagePanel(store.error.orEmpty(), { scope.launch { store.load(more = store.items.isNotEmpty()) } })
                }} else null, onApproachEnd = ::loadMore)
        }
    }
    if (filtersOpen) CatalogFilterView(kind, store.filters, store::genres,
        onApply = { store.filters = it; filtersOpen = false },
        onDismiss = { filtersOpen = false })
}
