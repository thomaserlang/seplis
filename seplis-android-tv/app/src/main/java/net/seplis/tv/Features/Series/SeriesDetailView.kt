package net.seplis.tv.features.series

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import kotlinx.coroutines.launch
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.cast.CastRow
import net.seplis.tv.features.library.MediaDetailDescription
import net.seplis.tv.features.library.MediaDetailLayout
import net.seplis.tv.features.library.MediaDetailHeader
import net.seplis.tv.features.library.MediaStateActions
import net.seplis.tv.features.playback.PlaybackTarget
import net.seplis.tv.components.MessagePanel
import net.seplis.tv.components.Palette
import net.seplis.tv.components.TvButton

@Composable
fun SeriesDetailView(ref: MediaReference, api: ApiClient, onEpisodes: (Series, Int?) -> Unit,
    onPlay: (PlaybackTarget) -> Unit, refresh: Int) {
    val model = remember(ref, api) { SeriesDetailModel(ref, api) }
    val scope = rememberCoroutineScope()
    val primaryFocus = remember { FocusRequester() }

    LaunchedEffect(ref, refresh) { model.load() }
    val current = model.series
    if (current == null) {
        if (model.error == null) net.seplis.tv.features.library.MediaDetailLoading()
        else MessagePanel(model.error.orEmpty(), retry = { scope.launch { model.load() } })
        return
    }
    LaunchedEffect(current.id) { primaryFocus.requestFocus() }
    MediaDetailLayout(current.poster, header = {
        MediaDetailHeader(current)
    }) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            MediaDetailDescription(current)
            MediaStateActions(current.watchlist, current.favorite,
                onWatchlist = { scope.launch { model.toggleWatchlist() } },
                onFavorite = { scope.launch { model.toggleFavorite() } },
                watchlistModifier = if (model.next?.canPlay != true && model.last?.canPlay != true)
                    Modifier.focusRequester(primaryFocus) else Modifier, enabled = !model.isUpdating)
            if (model.next != null || model.last != null) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    model.next?.let { episode ->
                        EpisodeActionsView(episode.watchHeading,
                            episode, modifier = Modifier.weight(1f), isUpdating = model.isUpdating,
                            playFocusRequester = if (episode.canPlay) primaryFocus else null,
                            onPlay = { fromBeginning -> onPlay(PlaybackTarget(ref, current.title, episode, fromBeginning)) },
                            onWatched = { increment -> scope.launch {
                                model.changeWatched(episode, increment)
                            } })
                    }
                    model.last?.let { episode ->
                        EpisodeActionsView("Last watched", episode, forceRewatch = true,
                            modifier = Modifier.weight(1f), isUpdating = model.isUpdating,
                            playFocusRequester = if (model.next?.canPlay != true && episode.canPlay) primaryFocus else null,
                            onPlay = { onPlay(PlaybackTarget(ref, current.title, episode, true)) },
                            onWatched = { increment -> scope.launch {
                                model.changeWatched(episode, increment)
                            } })
                    }
                    if (model.next == null || model.last == null) Spacer(Modifier.weight(1f))
                }
            }
        }
        CastRow(ref, api)
        if (current.seasons.isEmpty()) TvButton("All Episodes", { onEpisodes(current, null) })
        else {
            BoxWithConstraints {
            val columns = ((maxWidth.value + 12) / 182).toInt().coerceAtLeast(1)
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            current.seasons.chunked(columns).forEach { pair ->
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    pair.forEach { season ->
                        TvButton("Season ${season.number}", { onEpisodes(current, season.number) },
                            Modifier.weight(1f), subtitle = "${season.total} episodes")
                    }
                    repeat(columns - pair.size) { Spacer(Modifier.weight(1f)) }
                }
            }
            }
            }
        }
        model.error?.let { MessagePanel(it, retry = { scope.launch { model.load() } }) }
        Spacer(Modifier.height(12.dp))
    }
}
