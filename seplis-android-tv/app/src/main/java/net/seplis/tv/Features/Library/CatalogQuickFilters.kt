package net.seplis.tv.features.library

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.unit.dp
import net.seplis.tv.components.Palette
import net.seplis.tv.components.TvButton

@Composable
fun CatalogQuickFilters(kind: MediaKind, filters: CatalogFilters, focus: FocusRequester,
    onChange: (CatalogFilters) -> Unit, onUp: () -> Unit, showSettings: () -> Unit) {
    Row(Modifier.padding(horizontal = 16.dp).padding(top = 2.dp, bottom = 2.dp),
        horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        TvButton("Filters", showSettings, Modifier.focusRequester(focus), icon = Icons.Default.FilterList, onUp = onUp)
        TvButton("Available", { onChange(filters.copy(available = if (filters.available == FilterChoice.YES) FilterChoice.ANY else FilterChoice.YES)) },
            selected = filters.available == FilterChoice.YES, color = Palette.filterSelected, onUp = onUp)
        TvButton("New", { onChange(filters.copy(sort = CatalogFilters.newSort(kind))) },
            selected = filters.sort == CatalogFilters.newSort(kind), color = Palette.filterSelected, onUp = onUp)
        TvButton("Popular", { onChange(filters.copy(sort = "popularity_desc")) },
            selected = filters.sort == "popularity_desc", color = Palette.filterSelected, onUp = onUp)
        TvButton("Not Watched", { onChange(filters.copy(watched = if (filters.watched == FilterChoice.NO) FilterChoice.ANY else FilterChoice.NO)) },
            selected = filters.watched == FilterChoice.NO, color = Palette.filterSelected, onUp = onUp)
        TvButton("Watchlist", { onChange(filters.copy(watchlist = if (filters.watchlist == FilterChoice.YES) FilterChoice.ANY else FilterChoice.YES)) },
            selected = filters.watchlist == FilterChoice.YES, color = Palette.filterSelected, onUp = onUp)
        TvButton("Favorites", { onChange(filters.copy(favorites = if (filters.favorites == FilterChoice.YES) FilterChoice.ANY else FilterChoice.YES)) },
            selected = filters.favorites == FilterChoice.YES, color = Palette.filterSelected, onUp = onUp)
    }
}
