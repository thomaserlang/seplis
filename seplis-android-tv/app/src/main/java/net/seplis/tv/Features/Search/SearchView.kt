package net.seplis.tv.features.search

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.grid.rememberLazyGridState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import androidx.compose.runtime.withFrameNanos
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.type
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.components.FailureView
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.MediaPosterGrid
import net.seplis.tv.components.MediaPosterItem

@Composable
fun SearchView(store: SearchModel, refresh: Int, contentEntry: Int,
    onMenuFocus: () -> Unit, onOpen: (MediaReference) -> Unit, isActive: Boolean = true) {
    var query by remember { mutableStateOf("") }
    var loadedQuery by remember { mutableStateOf<String?>(null) }
    var focusedKey by remember(query) { mutableStateOf<String?>(null) }
    var restoreFocusPending by remember { mutableStateOf(false) }
    LaunchedEffect(refresh) { if (isActive && refresh > 0) restoreFocusPending = true }
    val searchFocus = remember { FocusRequester() }
    val scope = rememberCoroutineScope()
    val gridState = rememberLazyGridState()
    LaunchedEffect(contentEntry) {
        if (contentEntry > 0) { withFrameNanos { }; searchFocus.requestFocus() }
    }
    LaunchedEffect(query) {
        if (loadedQuery == query) return@LaunchedEffect
        store.search(query)
        loadedQuery = query
    }
    Column(Modifier.fillMaxSize()) {
        BasicTextField(query, { query = it },
            modifier = Modifier.fillMaxWidth().padding(horizontal = LibraryStyle.horizontalInset, vertical = 6.dp)
                .focusRequester(searchFocus)
                .onPreviewKeyEvent {
                    if (it.type == KeyEventType.KeyDown && it.key == Key.DirectionUp) {
                        onMenuFocus(); true
                    } else false
                }
                .background(LibraryStyle.controlBackground, RoundedCornerShape(6.dp))
                .border(1.dp, LibraryStyle.outline, RoundedCornerShape(6.dp))
                .padding(horizontal = 18.dp, vertical = 14.dp),
            singleLine = true, keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
            textStyle = TextStyle(color = Color.White, fontSize = 17.sp),
            decorationBox = { inner ->
                if (query.isEmpty()) Text("Search movies and series", color = LibraryStyle.muted, fontSize = 17.sp)
                inner()
            })
        val empty = !store.isLoading && loadedQuery == query &&
            store.results.isEmpty() && query.isNotBlank()
        MediaPosterGrid(store.results.map { MediaPosterItem(it.reference, it.title, it.poster) },
            isLoading = store.isLoading, state = gridState, refresh = refresh,
            restoreKey = focusedKey.takeIf { restoreFocusPending },
            onRestored = { restoreFocusPending = false },
            onFocus = { _, item -> focusedKey = item.key },
            onUp = { searchFocus.requestFocus() }, onOpen = onOpen,
            footer = if (empty || store.error != null) {{
                if (store.error != null) FailureView(store.error ?: "Search failed", retry = { scope.launch { store.search(query) } })
                else FailureView("No results for \"${query.trim()}\"")
            }} else null)
    }
}
