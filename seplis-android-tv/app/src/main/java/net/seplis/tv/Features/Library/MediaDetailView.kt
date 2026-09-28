package net.seplis.tv.features.library

import androidx.compose.runtime.Composable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.focusable
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.tv.material3.Text
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.movie.MovieDetailView
import net.seplis.tv.features.series.SeriesDetailView
import net.seplis.tv.features.playback.PlaybackTarget

@Composable
fun MediaDetailView(reference: MediaReference, api: APIClient,
    onEpisodes: (net.seplis.tv.features.series.Series, Int?) -> Unit, onPlay: (PlaybackTarget) -> Unit,
    refresh: Int) {
    when (reference.kind) {
        MediaKind.MOVIE -> MovieDetailView(reference, api, onPlay, refresh)
        MediaKind.SERIES -> SeriesDetailView(reference, api, onEpisodes, onPlay, refresh)
    }
}

@Composable
fun MediaDetailLoading(label: String = "Loading title") {
    Box(Modifier.fillMaxSize().focusable(), contentAlignment = Alignment.Center) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            CircularProgressIndicator(Modifier.size(20.dp), color = Color.White, strokeWidth = 2.dp)
            Text(label)
        }
    }
}
