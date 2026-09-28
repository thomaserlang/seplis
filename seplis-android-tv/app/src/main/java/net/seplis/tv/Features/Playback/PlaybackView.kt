package net.seplis.tv.features.playback

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.media3.ui.PlayerView
import androidx.tv.material3.Text
import kotlinx.coroutines.launch
import net.seplis.tv.app.SessionFactory
import net.seplis.tv.components.TvButton
import net.seplis.tv.core.networking.APIClient

@Composable
@androidx.annotation.OptIn(androidx.media3.common.util.UnstableApi::class)
fun PlaybackView(target: PlaybackTarget, api: APIClient, profileId: String,
    onClose: () -> Unit, onFinished: () -> Unit, onNext: (PlaybackTarget) -> Unit) {
    val context = LocalContext.current
    val finished by rememberUpdatedState(onFinished)
    var restartVersion by remember(target, api) { mutableIntStateOf(0) }
    val model = remember(target, api, restartVersion) {
        PlaybackModel(context, target, api, profileId, { finished() }, SessionFactory.playServer())
    }
    val scope = rememberCoroutineScope()
    var menu by remember(model) { mutableStateOf<PlaybackMenu?>(null) }
    var nativeView by remember { mutableStateOf<PlayerView?>(null) }
    var transitioning by remember(model) { mutableStateOf(false) }
    val errorFocus = remember { FocusRequester() }
    val lifecycle = LocalLifecycleOwner.current.lifecycle

    fun close() {
        if (transitioning) return
        transitioning = true
        scope.launch { model.stop(); onClose() }
    }
    val currentClose by rememberUpdatedState(::close)
    LaunchedEffect(model) { model.start() }
    DisposableEffect(model) { onDispose { model.dispose() } }
    DisposableEffect(lifecycle) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_STOP) currentClose()
        }
        lifecycle.addObserver(observer)
        onDispose { lifecycle.removeObserver(observer) }
    }
    LaunchedEffect(model.error) { if (model.error != null) errorFocus.requestFocus() }
    BackHandler { if (menu != null) menu = null else close() }

    fun openMenu(page: PlaybackMenu) {
        nativeView?.controllerShowTimeoutMs = 0
        menu = page
    }

    Box(Modifier.fillMaxSize().background(Color.Black)) {
        NativePlayerView(model, Modifier.fillMaxSize(), onReady = { nativeView = it },
            onSettings = { openMenu(PlaybackMenu.SETTINGS) },
            onSubtitles = { openMenu(PlaybackMenu.SUBTITLES) },
            onNext = {
                model.nextEpisode?.takeUnless { transitioning }?.let { episode ->
                    transitioning = true
                    scope.launch {
                        model.stop()
                        onNext(PlaybackTarget(target.reference, target.title, episode, true))
                    }
                }
            })
        if (model.error != null) {
            Column(Modifier.align(Alignment.Center).background(Color.Black.copy(alpha = 0.9f)).padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(model.error.orEmpty())
                TvButton("Retry", {
                    if (!transitioning) {
                        transitioning = true
                        scope.launch {
                            model.stop()
                            restartVersion++
                        }
                    }
                }, Modifier.focusRequester(errorFocus))
                TvButton("Back", ::close)
            }
        } else if (model.isLoading) {
            Box(Modifier.fillMaxSize().background(Color.Black), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = Color.White)
            }
        }
    }
    menu?.let { initial ->
        PlaybackSettings(model, initial) {
            menu = null
            nativeView?.apply {
                controllerShowTimeoutMs = 5_000
                showController()
                findViewById<android.view.View>(if (initial == PlaybackMenu.SUBTITLES)
                    androidx.media3.ui.R.id.exo_subtitle else androidx.media3.ui.R.id.exo_settings)?.requestFocus()
            }
        }
    }
    model.preferences.error?.let { message ->
        androidx.compose.ui.window.Dialog(onDismissRequest = { model.preferences.error = null }) {
            Column(Modifier.background(Color.Black).padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Playback preferences")
                Text(message)
                TvButton("OK", { model.preferences.error = null })
            }
        }
    }
}
