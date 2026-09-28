package net.seplis.tv.features.movie

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.key
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.cast.CastRow
import net.seplis.tv.features.library.MediaDetailDescription
import net.seplis.tv.features.library.MediaDetailLayout
import net.seplis.tv.features.library.MediaDetailHeader
import net.seplis.tv.features.library.MediaStateActions
import net.seplis.tv.components.WatchedButton
import net.seplis.tv.features.playback.PlaybackAction
import net.seplis.tv.features.playback.PlaybackTarget
import net.seplis.tv.components.FailureView
import net.seplis.tv.components.TvButton

@Composable
fun MovieDetailView(reference: MediaReference, api: APIClient, onPlay: (PlaybackTarget) -> Unit, refresh: Int) {
    var model by remember(reference, api) { mutableStateOf(MovieDetailModel(reference, api)) }
    key(model.reference) {
        MovieDetailContent(model, api, onPlay, refresh) { selected ->
            model = MovieDetailModel(selected, api)
        }
    }
}

@Composable
private fun MovieDetailContent(model: MovieDetailModel, api: APIClient, onPlay: (PlaybackTarget) -> Unit,
    refresh: Int, onOpen: (MediaReference) -> Unit) {
    val ref = model.reference
    val scope = rememberCoroutineScope()
    val playFocus = remember { FocusRequester() }

    LaunchedEffect(ref, refresh) { model.load() }
    val current = model.movie
    if (current == null) {
        if (model.error == null) net.seplis.tv.features.library.MediaDetailLoading()
        else FailureView(model.error.orEmpty(), retry = { scope.launch { model.load() } })
        return
    }
    LaunchedEffect(current.id) { playFocus.requestFocus() }
    MediaDetailLayout(current.poster, header = {
        MediaDetailHeader(current)
    }) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            MediaDetailDescription(current)
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                val action = PlaybackAction.from(current.watched)
                TvButton(action.label, { onPlay(PlaybackTarget(ref, current.title,
                    fromBeginning = action.fromBeginning)) }, modifier = if (model.canPlay) Modifier.focusRequester(playFocus) else Modifier, enabled = model.canPlay,
                    icon = action.icon)
                WatchedButton(current.watched,
                    { scope.launch { model.changeWatched(true) } },
                    { scope.launch { model.changeWatched(false) } }, current.runtime, enabled = !model.isUpdating)
                MediaStateActions(current.watchlist, current.favorite,
                    onWatchlist = { scope.launch { model.toggleWatchlist() } },
                    onFavorite = { scope.launch { model.toggleFavorite() } },
                    watchlistModifier = if (model.canPlay) Modifier else Modifier.focusRequester(playFocus),
                    enabled = !model.isUpdating)
            }
        }
        CastRow(ref, api)
        current.collection?.let { group ->
            MovieCollectionView(group, api, current.id, onOpen)
        }
        model.error?.let { FailureView(it, retry = { scope.launch { model.load() } }) }
        Spacer(Modifier.height(12.dp))
    }
}
