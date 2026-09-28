package net.seplis.tv.app

import androidx.compose.foundation.focusGroup
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.focus.focusProperties
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.layout.layout

@Composable
internal fun RetainedPage(active: Boolean, focus: FocusRequester, restoreFocusOnActivate: Boolean = true,
    content: @Composable () -> Unit) {
    var wasActive by remember { mutableStateOf(false) }
    var hasFocus by remember { mutableStateOf(false) }
    LaunchedEffect(active) {
        if (restoreFocusOnActivate && active && !wasActive) {
            withFrameNanos { }
            if (!hasFocus && !focus.restoreFocusedChild()) focus.requestFocus()
        }
        wasActive = active
    }
    // Keep the back stack mounted, while excluding covered pages from focus and accessibility.
    Box(Modifier.fillMaxSize()
        .alpha(if (active) 1f else 0f)
        .layout { measurable, constraints ->
            val placeable = measurable.measure(constraints)
            layout(placeable.width, placeable.height) { if (active) placeable.place(0, 0) }
        }
        .then(if (active) Modifier else Modifier.clearAndSetSemantics {})
        .focusProperties { onEnter = { if (!active) cancelFocusChange() } }
        .onFocusChanged { hasFocus = it.hasFocus }.focusRequester(focus).focusGroup()) { content() }
}
