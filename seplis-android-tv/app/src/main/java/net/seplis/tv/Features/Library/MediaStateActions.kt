package net.seplis.tv.features.library

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.outlined.BookmarkBorder
import androidx.compose.material.icons.outlined.StarBorder
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.MediaStateButton

@Composable
fun MediaStateActions(watchlist: Boolean, favorite: Boolean,
    onWatchlist: () -> Unit, onFavorite: () -> Unit, watchlistModifier: Modifier = Modifier,
    enabled: Boolean = true) {
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        MediaStateButton("Watchlist", if (watchlist) Icons.Filled.Bookmark else Icons.Outlined.BookmarkBorder,
            watchlist, LibraryStyle.purple, onWatchlist, modifier = watchlistModifier, enabled = enabled)
        MediaStateButton("Favorite", if (favorite) Icons.Filled.Star else Icons.Outlined.StarBorder,
            favorite, LibraryStyle.gold, onFavorite, enabled = enabled)
    }
}
