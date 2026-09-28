package net.seplis.tv.features.movie

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.unit.dp
import androidx.tv.material3.Text
import kotlinx.coroutines.launch
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.cast.CastRow
import net.seplis.tv.features.library.MediaDetailDescription
import net.seplis.tv.features.library.MediaDetailLayout
import net.seplis.tv.features.library.MediaDetailHeader
import net.seplis.tv.features.library.MediaStateActions
import net.seplis.tv.components.WatchedButton
import net.seplis.tv.features.playback.PlaybackAction
import net.seplis.tv.features.playback.PlaybackTarget
import net.seplis.tv.components.MessagePanel
import net.seplis.tv.components.Palette
import net.seplis.tv.components.TvButton

@Composable
fun MovieDetailView(ref: MediaReference, api: ApiClient, onPlay: (PlaybackTarget) -> Unit,
    onOpen: (MediaReference) -> Unit, refresh: Int) {
    val model = remember(ref, api) { MovieDetailModel(ref, api) }
    val scope = rememberCoroutineScope()
    val playFocus = remember { FocusRequester() }

    LaunchedEffect(ref, refresh) { model.load() }
    val current = model.movie
    if (current == null) {
        if (model.error == null) net.seplis.tv.features.library.MediaDetailLoading()
        else MessagePanel(model.error.orEmpty(), retry = { scope.launch { model.load() } })
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
        model.error?.let { MessagePanel(it, retry = { scope.launch { model.load() } }) }
        Spacer(Modifier.height(12.dp))
    }
}
