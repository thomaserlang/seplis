package net.seplis.tv.features.profiles

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.PersonAdd
import androidx.compose.material.icons.filled.Replay
import androidx.compose.material3.Icon
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.tv.material3.Text
import kotlinx.coroutines.launch
import net.seplis.tv.app.AppSession
import net.seplis.tv.app.SessionState
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.TvButton
import net.seplis.tv.core.security.Profile
import net.seplis.tv.features.authentication.DeviceLoginView

@Composable
fun ProfilesView(session: AppSession, onBack: () -> Unit) {
    var adding by remember { mutableStateOf(false) }
    var removing by remember { mutableStateOf<Profile?>(null) }
    val scope = rememberCoroutineScope()
    val first = remember { FocusRequester() }
    val active = (session.state as? SessionState.Active)?.profile
    BackHandler { onBack() }
    Column(Modifier.fillMaxSize().background(LibraryStyle.background).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)) {
        Text("Profiles", fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
        LazyVerticalGrid(GridCells.Adaptive(120.dp), Modifier.weight(1f),
            contentPadding = PaddingValues(10.dp),
            horizontalArrangement = Arrangement.spacedBy(14.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
            itemsIndexed(session.profiles, key = { _, profile -> profile.id }) { index, profile ->
                var focused by remember { mutableStateOf(false) }
                Column(Modifier.widthIn(max = 140.dp).height(105.dp)
                    .then(if (index == 0) Modifier.focusRequester(first) else Modifier)
                    .background(LibraryStyle.controlBackground, RoundedCornerShape(4.dp))
                    .border(1.5.dp, if (focused) Color.White else Color.Transparent, RoundedCornerShape(4.dp))
                    .onFocusChanged { focused = it.isFocused }
                    .combinedClickable(
                        onClick = { if (session.needsSignIn(profile)) adding = true else session.switch(profile) },
                        onLongClick = { removing = profile }),
                    horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                    Icon(Icons.Default.AccountCircle, null, tint = Color.White, modifier = Modifier.size(36.dp))
                    Spacer(Modifier.height(10.dp))
                    Text(profile.username, maxLines = 1, fontSize = 14.sp)
                    Text(if (session.needsSignIn(profile)) "Sign in again" else if (profile.id == active?.id) "Active" else " ",
                        fontSize = 10.sp, color = LibraryStyle.muted)
                }
            }
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterHorizontally)) {
            TvButton("Add Account", { adding = true },
                if (session.profiles.isEmpty()) Modifier.focusRequester(first) else Modifier, icon = Icons.Default.PersonAdd)
            active?.let { TvButton("Sign Out of ${it.username}", { removing = it }) }
            if (session.hasPendingSignIn) TvButton("Finish Sign In", { scope.launch { session.retryPendingSignIn() } }, icon = Icons.Default.Replay)
        }
    }
    LaunchedEffect(session.profiles) { withFrameNanos { }; first.requestFocus() }
    if (adding) Dialog(onDismissRequest = { adding = false }, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Box(Modifier.fillMaxSize().background(LibraryStyle.background)) {
            DeviceLoginView(session, onBack = { adding = false }, onSignedIn = { adding = false })
        }
    }
    removing?.let { profile ->
        Dialog(onDismissRequest = { removing = null }) {
            Column(Modifier.background(LibraryStyle.controlBackground, RoundedCornerShape(4.dp)).padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Remove ${profile.username} from this TV?")
                TvButton("Remove Account", { session.remove(profile); removing = null })
                TvButton("Cancel", { removing = null })
            }
        }
    }
}
