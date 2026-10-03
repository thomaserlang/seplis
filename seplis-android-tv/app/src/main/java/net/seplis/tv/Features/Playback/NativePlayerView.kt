package net.seplis.tv.features.playback

import android.view.Gravity
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageButton
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.Switch
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.media3.ui.PlayerControlView
import androidx.media3.ui.PlayerView
import androidx.tv.material3.Text
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.TvButton

@androidx.annotation.OptIn(androidx.media3.common.util.UnstableApi::class)
@Composable
fun NativePlayerView(model: PlaybackModel, modifier: Modifier = Modifier,
    onSettings: () -> Unit, onSubtitles: () -> Unit, onNext: () -> Unit,
    onReady: (PlayerView) -> Unit) {
    val settings by rememberUpdatedState(onSettings)
    val subtitles by rememberUpdatedState(onSubtitles)
    val playNext by rememberUpdatedState(onNext)
    key(model.target) {
    AndroidView(modifier = modifier, factory = { context ->
        PlayerView(context).apply {
            isFocusable = true
            isFocusableInTouchMode = true
            setControllerVisibilityListener(PlayerView.ControllerVisibilityListener { visibility ->
                if (visibility != View.VISIBLE) requestFocus()
            })
            controllerShowTimeoutMs = 5_000
            setControllerAnimationEnabled(false)
            setShowNextButton(false)
            setShowPreviousButton(false)
            setShowSubtitleButton(true)
            findViewById<View>(androidx.media3.ui.R.id.exo_settings).setOnClickListener { settings() }
            findViewById<View>(androidx.media3.ui.R.id.exo_subtitle).apply {
                contentDescription = "Subtitles"
                setOnClickListener { subtitles() }
            }
            val controls = findViewById<LinearLayout>(androidx.media3.ui.R.id.exo_basic_controls)
            val buttonBackground = findViewById<View>(androidx.media3.ui.R.id.exo_settings).background
            val next = ImageButton(context).apply {
                id = net.seplis.tv.R.id.playback_next_episode
                contentDescription = "Next Episode"
                setImageResource(androidx.media3.ui.R.drawable.exo_styled_controls_next)
                background = buttonBackground?.constantState?.newDrawable()
                setOnClickListener { playNext() }
                val size = (48 * resources.displayMetrics.density).toInt()
                layoutParams = LinearLayout.LayoutParams(size, size)
            }
            controls.addView(next, 0)
            val density = resources.displayMetrics.density
            val metadata = LinearLayout(context).apply {
                orientation = LinearLayout.VERTICAL
                addView(TextView(context).apply {
                    text = model.target.title
                    textSize = 22f
                    setTextColor(android.graphics.Color.WHITE)
                })
                model.target.episode?.let { episode -> addView(TextView(context).apply {
                    text = episode.label
                    textSize = 14f
                    setTextColor(android.graphics.Color.LTGRAY)
                }) }
            }
            findViewById<PlayerControlView>(androidx.media3.ui.R.id.exo_controller).addView(metadata,
                FrameLayout.LayoutParams(FrameLayout.LayoutParams.WRAP_CONTENT, FrameLayout.LayoutParams.WRAP_CONTENT,
                    Gravity.BOTTOM or Gravity.START).apply {
                    leftMargin = (32 * density).toInt()
                    bottomMargin = (90 * density).toInt()
                })
            onReady(this)
        }
    }, update = { view ->
        if (view.player !== model.player) {
            view.player = model.player
            if (model.player != null) {
                view.showController()
                view.post { view.findViewById<View>(androidx.media3.ui.R.id.exo_play_pause).requestFocus() }
            }
        }
        view.findViewById<View>(net.seplis.tv.R.id.playback_next_episode).visibility =
            if (model.nextEpisode != null) View.VISIBLE else View.GONE
        view.findViewById<View>(androidx.media3.ui.R.id.exo_subtitle).isEnabled =
            model.candidates.getOrNull(model.selectedSource)?.source?.subtitles?.isNotEmpty() == true
    }, onRelease = { it.player = null })
    }
}

enum class PlaybackMenu(val title: String) {
    SETTINGS("Settings"), SOURCE("Source"), QUALITY("Quality"), AUDIO("Audio"),
    SUBTITLES("Subtitles"), MEDIA_INFO("Media Info"), DECISION("Playback Decision")
}

@Composable
fun PlaybackSettings(model: PlaybackModel, initial: PlaybackMenu, onDismiss: () -> Unit) {
    val pages = remember { mutableStateListOf(initial) }
    val page = pages.last()
    val focus = remember(page) { FocusRequester() }
    val candidate = model.candidates.getOrNull(model.selectedSource)
    val source = candidate?.source
    val hasInfo = !model.isLoading && model.error == null && candidate != null
    fun back() { if (pages.size > 1) pages.removeAt(pages.lastIndex) else onDismiss() }
    Dialog(onDismissRequest = ::back, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        BackHandler { back() }
        Box(Modifier.fillMaxSize().padding(24.dp), contentAlignment = Alignment.CenterEnd) {
            Column(Modifier.width(360.dp).fillMaxHeight().background(LibraryStyle.controlBackground, RoundedCornerShape(8.dp))
                .padding(18.dp)) {
                Text(page.title, fontSize = 20.sp, lineHeight = 24.sp, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(12.dp))
                key(page) {
                    Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()),
                        verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        when (page) {
                            PlaybackMenu.SETTINGS -> {
                                if (candidate != null) MenuRow("Source", candidate.label,
                                    Modifier.focusRequester(focus)) { pages.add(PlaybackMenu.SOURCE) }
                                MenuRow("Quality", PlaybackQuality.label(model.preferences.maxBitrate, source?.bitrate),
                                    if (candidate == null) Modifier.focusRequester(focus) else Modifier) {
                                    pages.add(PlaybackMenu.QUALITY)
                                }
                                if (hasInfo) MenuRow("Media Info", "") { pages.add(PlaybackMenu.MEDIA_INFO) }
                                if (hasInfo) MenuRow("Playback Decision", PlaybackInfoMenu.method(model.session?.decision)) { pages.add(PlaybackMenu.DECISION) }
                                ToggleRow("HDR", model.preferences.hdrEnabled, !model.isLoading) { model.setHDR(it) }
                                ToggleRow("Force Transcode", model.forceTranscode, !model.isLoading) { model.changeForceTranscode(it) }
                                if ((source?.audio?.size ?: 0) > 1) MenuRow("Audio",
                                    source?.audio?.firstOrNull { it.key == model.selectedAudio }?.title.orEmpty()) { pages.add(PlaybackMenu.AUDIO) }
                            }
                            PlaybackMenu.SOURCE -> model.candidates.forEachIndexed { index, item ->
                                ChoiceRow("${index + 1}. ${item.label}", index == model.selectedSource,
                                    if (index == model.selectedSource) Modifier.focusRequester(focus) else Modifier) {
                                    model.selectSource(index); onDismiss()
                                }
                            }
                            PlaybackMenu.QUALITY -> PlaybackQuality.available(source?.bitrate, model.preferences.maxBitrate).forEach { bitrate ->
                                ChoiceRow(PlaybackQuality.label(bitrate, source?.bitrate), bitrate == model.preferences.maxBitrate,
                                    if (bitrate == model.preferences.maxBitrate) Modifier.focusRequester(focus) else Modifier) {
                                    model.selectBitrate(bitrate); onDismiss()
                                }
                            }
                            PlaybackMenu.AUDIO -> source?.audio?.forEach { stream ->
                                ChoiceRow(stream.title, stream.key == model.selectedAudio,
                                    if (stream.key == model.selectedAudio) Modifier.focusRequester(focus) else Modifier) {
                                    model.selectAudio(stream.key); onDismiss()
                                }
                            }
                            PlaybackMenu.SUBTITLES -> {
                                ChoiceRow("Off", model.selectedSubtitle == null,
                                    if (model.selectedSubtitle == null) Modifier.focusRequester(focus) else Modifier) {
                                    model.selectSubtitle(null); onDismiss()
                                }
                                source?.subtitles?.forEach { stream ->
                                    ChoiceRow(stream.title, stream.key == model.selectedSubtitle,
                                        if (stream.key == model.selectedSubtitle) Modifier.focusRequester(focus) else Modifier) {
                                        model.selectSubtitle(stream.key); onDismiss()
                                    }
                                }
                            }
                            PlaybackMenu.MEDIA_INFO, PlaybackMenu.DECISION -> {
                                val rows = if (page == PlaybackMenu.DECISION)
                                    PlaybackInfoMenu.decision(model.session?.decision, candidate?.request?.url)
                                else source?.let { PlaybackInfoMenu.source(it, model.selectedAudio) }.orEmpty()
                                rows.forEachIndexed { index, (label, value) ->
                                    PlaybackInfoRow(label, value, if (index == 0) Modifier.focusRequester(focus) else Modifier)
                                }
                            }
                        }
                    }
                }
                Spacer(Modifier.height(8.dp))
                TvButton(if (pages.size == 1) "Close" else "Back", ::back)
            }
        }
        LaunchedEffect(page) { focus.requestFocus() }
    }
}

@Composable
private fun MenuRow(label: String, value: String, modifier: Modifier = Modifier, onClick: () -> Unit) {
    TvButton(label, onClick, modifier.fillMaxWidth(), subtitle = value.takeIf { it.isNotBlank() })
}

@Composable
private fun ChoiceRow(label: String, selected: Boolean, modifier: Modifier = Modifier, onClick: () -> Unit) {
    TvButton(label, onClick, modifier.fillMaxWidth(), selected = selected, color = LibraryStyle.surfaceRaised,
        icon = if (selected) Icons.Default.Check else null)
}

@Composable
private fun ToggleRow(label: String, checked: Boolean, enabled: Boolean, modifier: Modifier = Modifier, onChange: (Boolean) -> Unit) {
    var focused by remember { mutableStateOf(false) }
    Row(modifier.fillMaxWidth().border(1.5.dp, if (focused) Color.White else Color.Transparent, RoundedCornerShape(4.dp))
        .onFocusChanged { focused = it.isFocused }
        .toggleable(checked, enabled = enabled, role = Role.Switch, onValueChange = onChange)
        .padding(horizontal = 12.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(label, Modifier.weight(1f), fontSize = 13.sp, lineHeight = 16.sp)
        Switch(checked, onCheckedChange = null, enabled = enabled)
    }
}
