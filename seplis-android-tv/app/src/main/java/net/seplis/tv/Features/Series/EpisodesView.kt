package net.seplis.tv.features.series

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.focusRestorer
import androidx.compose.foundation.background
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.series.Episode
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.MediaDetailLayout
import net.seplis.tv.features.playback.PlaybackTarget
import net.seplis.tv.components.MessagePanel
import net.seplis.tv.components.Palette
import androidx.tv.material3.Text

@Composable
fun EpisodesView(reference: MediaReference, series: Series, season: Int?, api: ApiClient,
    refresh: Int = 0,
    onPlay: (PlaybackTarget) -> Unit) {
    val model = remember(reference, season, api) { EpisodesModel(reference, season, api) }
    val scope = rememberCoroutineScope()
    val first = remember { FocusRequester() }
    LaunchedEffect(model, refresh) { model.load() }

    LaunchedEffect(model.episodes != null, model.error) {
        if (!model.episodes.isNullOrEmpty() && model.error == null) first.requestFocus()
    }
    MediaDetailLayout(series.poster, headerSpacing = 0.dp, scrollContent = false, header = {}) {
        when {
            model.error != null -> MessagePanel(model.error.orEmpty(), retry = { scope.launch { model.load() } })
            model.episodes == null -> net.seplis.tv.features.library.MediaDetailLoading("Loading episodes")
            model.episodes?.isEmpty() == true -> Text("No episodes available", color = Palette.muted)
            else -> LazyColumn(Modifier.fillMaxSize().focusRequester(first).focusRestorer(),
                contentPadding = PaddingValues(bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(model.episodes.orEmpty(), key = Episode::number) { episode ->
                    SeasonEpisodeRow(episode, model.isUpdating, onPlay = { fromBeginning ->
                        onPlay(PlaybackTarget(reference, series.title, episode, fromBeginning))
                    }, onIncrement = { scope.launch { model.changeWatched(episode, true) } },
                        onDecrement = { scope.launch { model.changeWatched(episode, false) } })
                }
            }
        }
    }
    model.updateError?.let { message ->
        androidx.compose.ui.window.Dialog(onDismissRequest = { model.updateError = null }) {
            Column(Modifier.background(Palette.surface, RoundedCornerShape(4.dp)).padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Could not update watched count")
                Text(message)
                net.seplis.tv.components.TvButton("OK", { model.updateError = null })
            }
        }
    }
}
