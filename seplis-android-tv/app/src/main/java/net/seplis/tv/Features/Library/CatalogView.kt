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
import net.seplis.tv.components.FailureView
import net.seplis.tv.components.MediaPosterGrid
import net.seplis.tv.components.MediaPosterItem

@Composable
fun CatalogView(kind: MediaKind, store: CatalogModel, refresh: Int, contentEntry: Int,
    onMenuFocus: () -> Unit, onOpen: (MediaReference) -> Unit, isActive: Boolean = true) {
    var filters by remember { mutableStateOf(CatalogFilters()) }
    var focusedID by remember(filters) { mutableStateOf<Int?>(null) }
    var restoreFocusPending by remember { mutableStateOf(false) }
    LaunchedEffect(refresh) { if (isActive && refresh > 0) restoreFocusPending = true }
    val scope = rememberCoroutineScope()
    val firstFilter = remember { FocusRequester() }
    val gridState = androidx.compose.runtime.key(filters) { rememberLazyGridState() }
    LaunchedEffect(contentEntry) {
        if (contentEntry > 0) { withFrameNanos { }; firstFilter.requestFocus() }
    }
    var filtersOpen by remember { mutableStateOf(false) }
    LaunchedEffect(filters) { store.load(filters) }
    fun loadMore() {
        if (store.cursor != null && store.error == null) scope.launch { store.load(filters, more = true) }
    }
    Column(Modifier.fillMaxSize()) {
        CatalogQuickFilters(kind, filters, firstFilter, { filters = it }, onMenuFocus) { filtersOpen = true }
        if (store.error != null && store.items.isEmpty()) {
            FailureView(store.error ?: "Could not load", { scope.launch { store.load(filters) } })
        } else {
            val empty = store.hasLoaded && !store.loading && store.items.isEmpty() && store.error == null
            MediaPosterGrid(store.items.map { MediaPosterItem(MediaReference(kind, it.id), it.title, it.poster) },
                isLoading = store.loading || !store.hasLoaded && store.error == null, state = gridState,
                refresh = refresh, restoreKey = focusedID?.takeIf { restoreFocusPending }?.let { "$kind-$it" },
                onRestored = { restoreFocusPending = false }, onFocus = { index, item ->
                    focusedID = item.reference.id
                    if (index >= store.items.size - 16) loadMore()
                }, onUp = { firstFilter.requestFocus() }, onOpen = onOpen,
                footer = if (empty || store.error != null) {{
                    if (empty) FailureView("No titles found")
                    else FailureView(store.error.orEmpty(), { scope.launch { store.load(filters, more = store.items.isNotEmpty()) } })
                }} else null, onApproachEnd = ::loadMore)
        }
    }
    if (filtersOpen) CatalogFilterView(kind, filters, store.api,
        onApply = { filters = it; filtersOpen = false },
        onDismiss = { filtersOpen = false })
}
