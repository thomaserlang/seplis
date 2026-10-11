package net.seplis.tv.features.library

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.unit.dp
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.TvButton

@Composable
fun CatalogQuickFilters(kind: MediaKind, filters: CatalogFilters, focus: FocusRequester,
    onChange: (CatalogFilters) -> Unit, onUp: () -> Unit, showSettings: () -> Unit) {
    Row(Modifier.padding(horizontal = LibraryStyle.horizontalInset).padding(top = 2.dp, bottom = 2.dp),
        horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        TvButton("Filters", showSettings, Modifier.focusRequester(focus), icon = Icons.Default.FilterList, onUp = onUp)
        TvButton("Available", { onChange(filters.copy(available = if (filters.available == CatalogChoice.YES) CatalogChoice.ANY else CatalogChoice.YES)) },
            selected = filters.available == CatalogChoice.YES, color = LibraryStyle.filterSelected, onUp = onUp)
        TvButton("New", { onChange(filters.copy(sort = CatalogFilters.newSort(kind))) },
            selected = filters.sort == CatalogFilters.newSort(kind), color = LibraryStyle.filterSelected, onUp = onUp)
        TvButton("Popular", { onChange(filters.copy(sort = "popularity_desc")) },
            selected = filters.sort == "popularity_desc", color = LibraryStyle.filterSelected, onUp = onUp)
        TvButton("Not Watched", { onChange(filters.copy(watched = if (filters.watched == CatalogChoice.NO) CatalogChoice.ANY else CatalogChoice.NO)) },
            selected = filters.watched == CatalogChoice.NO, color = LibraryStyle.filterSelected, onUp = onUp)
        TvButton("Watchlist", { onChange(filters.copy(watchlist = if (filters.watchlist == CatalogChoice.YES) CatalogChoice.ANY else CatalogChoice.YES)) },
            selected = filters.watchlist == CatalogChoice.YES, color = LibraryStyle.filterSelected, onUp = onUp)
        TvButton("Favorites", { onChange(filters.copy(favorites = if (filters.favorites == CatalogChoice.YES) CatalogChoice.ANY else CatalogChoice.YES)) },
            selected = filters.favorites == CatalogChoice.YES, color = LibraryStyle.filterSelected, onUp = onUp)
    }
}
