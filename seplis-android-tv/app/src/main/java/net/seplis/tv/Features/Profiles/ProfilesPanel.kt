package net.seplis.tv.features.profiles

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.PersonAdd
import androidx.compose.material.icons.filled.PersonRemove
import androidx.compose.material.icons.automirrored.filled.Logout
import androidx.compose.material.icons.filled.Replay
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.ChevronLeft
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.sp
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import androidx.compose.runtime.setValue
import androidx.compose.runtime.withFrameNanos
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.type
import androidx.compose.ui.unit.dp
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.window.DialogWindowProvider
import androidx.compose.ui.platform.LocalView
import androidx.compose.runtime.SideEffect
import androidx.tv.material3.Text
import net.seplis.tv.app.AppSession
import net.seplis.tv.core.security.Profile
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.TvButton
import net.seplis.tv.features.authentication.DeviceLoginView

@Composable
fun ProfilesPanel(session: AppSession, onClose: () -> Unit) {
    var addingAccount by remember { mutableStateOf(false) }
    var returnToAddAccount by remember { mutableStateOf(false) }
    var removing by remember { mutableStateOf(false) }
    var confirm by remember { mutableStateOf<Profile?>(null) }
    val first = remember { FocusRequester() }
    val addAccountFocus = remember { FocusRequester() }
    val removeFocus = remember { FocusRequester() }
    var returnToRemove by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val active = (session.state as? net.seplis.tv.app.SessionState.Active)?.profile
    val others = session.profiles.filter { it.id != active?.id }
    fun back() {
        if (addingAccount) addingAccount = false
        else if (confirm != null) confirm = null
        else if (removing) { returnToRemove = true; removing = false }
        else onClose()
    }
    Dialog(onDismissRequest = ::back, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        val window = (LocalView.current.parent as? DialogWindowProvider)?.window
        SideEffect { window?.setDimAmount(0f) }
        BackHandler { back() }
        if (addingAccount) {
            Box(Modifier.fillMaxSize().background(LibraryStyle.background)) {
                DeviceLoginView(session, onBack = { addingAccount = false }, onSignedIn = onClose)
            }
        } else Box(Modifier.fillMaxSize()) {
            Column(Modifier.align(Alignment.TopStart).padding(start = 16.dp, top = 8.dp, bottom = 16.dp)
                .width(240.dp).testTag("profiles-panel").background(LibraryStyle.controlBackground, RoundedCornerShape(4.dp))
                .border(0.5.dp, Color.White.copy(alpha = 0.15f), RoundedCornerShape(4.dp))
                .onPreviewKeyEvent {
                    if (it.key == Key.DirectionRight && it.type == KeyEventType.KeyDown) { onClose(); true } else false
                }
                .verticalScroll(rememberScrollState()).padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                if (removing) {
                    Text("Remove an Account", fontSize = 13.sp, fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.padding(bottom = 4.dp))
                    TvButton("Back", { returnToRemove = true; removing = false }, Modifier.fillMaxWidth().focusRequester(first),
                        icon = Icons.Default.ChevronLeft, alignStart = true)
                }
                (if (removing) others else session.profiles).forEach { profile ->
                    TvButton(profile.username, {
                        if (removing) confirm = profile
                        else if (session.needsSignIn(profile)) { returnToAddAccount = true; addingAccount = true }
                        else if (profile.id == active?.id) onClose()
                        else {
                            session.switch(profile)
                            if ((session.state as? net.seplis.tv.app.SessionState.Active)?.profile?.id == profile.id) onClose()
                        }
                    }, Modifier.fillMaxWidth().then(if (!removing && profile.id == active?.id) Modifier.focusRequester(first) else Modifier),
                        trailingText = if (!removing && session.needsSignIn(profile)) "Sign in again" else null,
                        icon = if (removing) Icons.Default.PersonRemove else Icons.Default.AccountCircle,
                        trailingIcon = if (!removing && profile.id == active?.id) Icons.Default.Check else null,
                        alignStart = true)
                }
                if (!removing) {
                    HorizontalDivider(Modifier.padding(vertical = 2.dp), color = Color.White.copy(alpha = 0.15f))
                    TvButton("Add Account", { returnToAddAccount = true; addingAccount = true },
                        Modifier.fillMaxWidth().focusRequester(addAccountFocus), icon = Icons.Default.PersonAdd, alignStart = true)
                    if (session.hasPendingSignIn) TvButton("Finish Sign In", {
                        scope.launch { session.retryPendingSignIn() }
                    }, Modifier.fillMaxWidth(), icon = Icons.Default.Replay, alignStart = true)
                    active?.let { profile -> TvButton("Sign Out of ${profile.username}", { confirm = profile }, Modifier.fillMaxWidth(),
                        icon = Icons.AutoMirrored.Filled.Logout, alignStart = true) }
                    if (others.isNotEmpty()) TvButton("Remove an Account", { removing = true }, Modifier.fillMaxWidth().focusRequester(removeFocus),
                        icon = Icons.Default.PersonRemove, alignStart = true)
                }
            }
        }
        androidx.compose.runtime.LaunchedEffect(addingAccount, removing) {
            if (!addingAccount) {
                withFrameNanos { }
                when {
                    removing -> first.requestFocus()
                    returnToRemove -> { removeFocus.requestFocus(); returnToRemove = false }
                    returnToAddAccount || active == null -> { addAccountFocus.requestFocus(); returnToAddAccount = false }
                    else -> first.requestFocus()
                }
            }
        }
    }
    confirm?.let { profile ->
        androidx.compose.ui.window.Dialog(onDismissRequest = { confirm = null }) {
            Column(Modifier.background(LibraryStyle.controlBackground, RoundedCornerShape(8.dp)).padding(22.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Remove ${profile.username} from this TV?")
                TvButton("Remove Account", { session.remove(profile); confirm = null; returnToAddAccount = true; removing = false })
                TvButton("Cancel", { confirm = null })
            }
        }
    }
}
