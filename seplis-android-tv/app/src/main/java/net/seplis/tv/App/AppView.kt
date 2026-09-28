package net.seplis.tv.app

import net.seplis.tv.shared.topshelf.*

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.tv.material3.Text
import net.seplis.tv.features.authentication.DeviceLoginView
import net.seplis.tv.features.profiles.ProfilesView
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.TvButton
import net.seplis.tv.features.topshelf.*

@Composable
fun AppView(session: AppSession, pendingLink: TopShelfLink? = null, consumeLink: () -> Unit = {}) {
    var browsingID by remember { mutableIntStateOf(0) }
    var launcherRevision by remember { mutableIntStateOf(0) }
    val context = androidx.compose.ui.platform.LocalContext.current.applicationContext
    val publisher = remember(context) {
        if (net.seplis.tv.BuildConfig.USE_FIXTURES) null else TopShelfPublisher(AndroidTopShelfStore(context))
    }
    val policy = remember { AppResumePolicy() }
    val lifecycle = androidx.lifecycle.compose.LocalLifecycleOwner.current.lifecycle
    androidx.compose.runtime.DisposableEffect(lifecycle) {
        val observer = androidx.lifecycle.LifecycleEventObserver { _, event ->
            val now = android.os.SystemClock.elapsedRealtime()
            if (event == androidx.lifecycle.Lifecycle.Event.ON_STOP) policy.background(now)
            if (event == androidx.lifecycle.Lifecycle.Event.ON_START) {
                if (policy.resume(now)) browsingID++
                launcherRevision++
            }
        }
        lifecycle.addObserver(observer)
        onDispose { lifecycle.removeObserver(observer) }
    }
    LaunchedEffect(session) { session.restore() }
    LaunchedEffect(Unit) { WatchHistory.changes.collect { launcherRevision++ } }
    LaunchedEffect(session.state, launcherRevision) {
        if (session.state != SessionState.Loading && session.state != SessionState.RestoreFailed) {
            val active = session.state as? SessionState.Active
            publisher?.refresh(active?.api, active?.profile?.id)
        }
    }
    androidx.compose.runtime.key(session, browsingID, (session.state as? SessionState.Active)?.api) {
        SessionContent(session, pendingLink, consumeLink)
    }
}

@Composable
private fun SessionContent(session: AppSession, pendingLink: TopShelfLink?, consumeLink: () -> Unit) {
    val scope = rememberCoroutineScope()
    val state = session.state
    val active = state as? SessionState.Active
    var presentedLink by remember { mutableStateOf<TopShelfLink?>(null) }
    LaunchedEffect(pendingLink, state) {
        if (pendingLink != null && state != SessionState.Loading) {
            consumeLink()
            if (active?.profile?.id == pendingLink.accountID) presentedLink = pendingLink
            else session.error = "Switch to the profile that owns this Continue Watching item, then select it again."
        }
    }
    Box(Modifier.fillMaxSize().background(LibraryStyle.background)) {
        when (state) {
            SessionState.Loading -> net.seplis.tv.components.FailureView("Loading profiles")
            SessionState.RestoreFailed -> net.seplis.tv.components.FailureView(
                "Saved profiles could not be loaded.", retry = { scope.launch { session.restore() } })
            SessionState.SignedOut -> DeviceLoginView(session, showsLogo = true)
            SessionState.ChooseProfile -> ProfilesView(session, onBack = session::returnToProfile)
            is SessionState.Active -> if (active != null) {
                val link = presentedLink
                if (link != null) TopShelfDestination(link, active.api,
                    onClose = { presentedLink = null }, onFinished = { presentedLink = null })
                else AppTabsView(session, active)
            }
        }
    }
    session.error?.let { message ->
        Dialog(onDismissRequest = { session.error = null }) {
            Column(Modifier.background(LibraryStyle.controlBackground, RoundedCornerShape(8.dp)).padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)) {
                Text(message)
                TvButton("OK", { session.error = null })
            }
        }
    }
}
