package net.seplis.tv.features.library

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.key
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.CancellationException
import net.seplis.tv.components.FailureView
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Replay
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.tv.material3.Text
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.TvButton

private enum class FilterPage(val label: String) {
    SORT("Sort"), LIBRARY("Library"), GENRES("Genres"), LANGUAGES("Languages"),
    YEAR("Year"), RATING("IMDb Rating"), VOTES("IMDb Votes")
}

@Composable
fun CatalogFilterView(kind: MediaKind, current: CatalogFilters, api: net.seplis.tv.core.networking.APIClient,
    onApply: (CatalogFilters) -> Unit,
    onDismiss: () -> Unit) {
    var draft by remember(current) { mutableStateOf(current) }
    var page by remember { mutableStateOf(FilterPage.SORT) }
    var genres by remember { mutableStateOf<List<CatalogGenre>>(emptyList()) }
    var genreError by remember { mutableStateOf<String?>(null) }
    var loadingGenres by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    suspend fun reloadGenres() {
        loadingGenres = true
        genreError = null
        try {
            val records = api.arrayAt("genres", mapOf("type" to kind.name.lowercase()))
            genres = (0 until records.length()).map { index ->
                val record = records.getJSONObject(index)
                CatalogGenre(record.getInt("id"), record.getString("name"))
            }
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { genreError = failure.message ?: "Could not load genres" }
        finally { loadingGenres = false }
    }
    LaunchedEffect(kind) { reloadGenres() }

    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(Modifier.fillMaxSize().background(LibraryStyle.background)
            .padding(horizontal = 32.dp, vertical = 20.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("Filters", fontSize = 18.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
                TvButton("Reset Filters", { draft = CatalogFilters() }, icon = Icons.Default.Replay)
                TvButton("Apply Filters", { onApply(draft) }, enabled = draft.validationError == null, icon = Icons.Default.Check)
                TvButton("Cancel", onDismiss, icon = Icons.Default.Close, iconOnly = true)
            }
            Row(horizontalArrangement = Arrangement.spacedBy(28.dp), modifier = Modifier.weight(1f)) {
                Column(Modifier.width(155.dp).verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    FilterPage.entries.forEach { item ->
                        TvButton(item.label, { page = item }, Modifier.fillMaxWidth(), selected = page == item,
                            color = LibraryStyle.filterSelected, trailingIcon = Icons.Default.ChevronRight, alignStart = true)
                    }
                }
                key(page) {
                Column(Modifier.weight(1f).verticalScroll(rememberScrollState()).padding(3.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(page.label, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
                    when (page) {
                        FilterPage.SORT -> CatalogFilters.sorts(kind).forEach { (label, value) ->
                            TvButton(label, { draft = draft.copy(sort = value) }, Modifier.fillMaxWidth(),
                                selected = draft.sort == value, color = LibraryStyle.filterSelected, alignStart = true,
                                trailingIcon = if (draft.sort == value) Icons.Default.Check else null)
                        }
                        FilterPage.LIBRARY -> {
                            FilterChoiceRow("Available to play", draft.available) { draft = draft.copy(available = it) }
                            FilterChoiceRow("On watchlist", draft.watchlist) { draft = draft.copy(watchlist = it) }
                            FilterChoiceRow("Favorite", draft.favorites) { draft = draft.copy(favorites = it) }
                            FilterChoiceRow("Watched", draft.watched) { draft = draft.copy(watched = it) }
                        }
                        FilterPage.GENRES -> {
                            genreError?.let { FailureView(it, retry = { scope.launch { reloadGenres() } }) }
                            if (loadingGenres) Text("Loading genres", color = LibraryStyle.muted)
                            genres.forEach { genre ->
                                FilterChoiceRow(genre.name, draft.genres[genre.id] ?: CatalogChoice.ANY,
                                    inclusiveLabels = true) { choice ->
                                    draft = draft.copy(genres = draft.genres + (genre.id to choice))
                                }
                            }
                        }
                        FilterPage.LANGUAGES -> FilterLanguagesView(draft.languages) { draft = draft.copy(languages = it) }
                        FilterPage.YEAR -> FilterRangeView("Year", draft.yearFrom, draft.yearTo,
                            { draft = draft.copy(yearFrom = it) }, { draft = draft.copy(yearTo = it) })
                        FilterPage.RATING -> FilterRangeView("IMDb rating", draft.ratingFrom, draft.ratingTo,
                            { draft = draft.copy(ratingFrom = it) }, { draft = draft.copy(ratingTo = it) })
                        FilterPage.VOTES -> FilterRangeView("IMDb votes", draft.votesFrom, draft.votesTo,
                            { draft = draft.copy(votesFrom = it) }, { draft = draft.copy(votesTo = it) })
                    }
                }
                }
            }
            draft.validationError?.let { Text(it, color = Color(0xFFEC7777)) }
        }
        }
    }
}
