package net.seplis.tv.features.topshelf

import net.seplis.tv.shared.topshelf.*

import androidx.activity.compose.BackHandler
import androidx.compose.runtime.*
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.core.networking.text
import net.seplis.tv.features.series.Episode
import net.seplis.tv.features.playback.*
import net.seplis.tv.components.FailureView

@Composable
fun TopShelfDestination(link: TopShelfLink, api: APIClient, onClose: () -> Unit, onFinished: () -> Unit) {
    if (!link.play) {
        net.seplis.tv.features.library.MediaDetailPresentation(link.reference, api, link.accountID.toString(), onClose)
        return
    }
    var target by remember(link) { mutableStateOf<PlaybackTarget?>(null) }
    var error by remember(link) { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()
    suspend fun load() {
        error = null
        try {
            val media = api.objectAt(link.reference.path)
            val episode = link.episodeNumber?.takeIf { link.reference.kind == net.seplis.tv.features.library.MediaKind.SERIES }
                ?.let { Episode.from(api.objectAt("${link.reference.path}/episodes/$it")) }
            target = PlaybackTarget(link.reference, media.text("title") ?: "Untitled", episode, false)
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) { error = failure.message ?: "Could not prepare video" }
    }
    LaunchedEffect(link) { load() }
    BackHandler { onClose() }
    val current = target
    if (current != null) PlaybackView(current, api, link.accountID.toString(), onClose, onFinished, onNext = { target = it })
    else FailureView(error ?: "Preparing video", retry = if (error == null) null else { { scope.launch { load() } } })
}
