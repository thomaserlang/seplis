package net.seplis.tv.features.authentication

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.Row
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import androidx.lifecycle.repeatOnLifecycle
import net.seplis.tv.app.AppSession
import net.seplis.tv.R
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.QRCodeView
import net.seplis.tv.components.TvButton

@Composable
fun DeviceLoginView(session: AppSession, onBack: (() -> Unit)? = null, onSignedIn: () -> Unit = {},
    showsLogo: Boolean = false) {
    val model = remember(session) { DeviceLoginModel(session) }
    var attempt by remember { mutableIntStateOf(0) }
    val authorization = model.authorization
    val error = model.error
    val lifecycle = androidx.lifecycle.compose.LocalLifecycleOwner.current.lifecycle
    val back = onBack ?: session::showProfiles
    BackHandler(enabled = onBack != null || session.profiles.isNotEmpty()) { back() }

    LaunchedEffect(attempt, lifecycle) {
        lifecycle.repeatOnLifecycle(androidx.lifecycle.Lifecycle.State.RESUMED) {
            if (model.run()) onSignedIn()
        }
    }

    Column(Modifier.fillMaxSize()
        .then(if (showsLogo) Modifier.background(Color.Black) else Modifier)
        .padding(horizontal = 30.dp, vertical = if (showsLogo) 30.dp else 50.dp),
        horizontalAlignment = Alignment.CenterHorizontally) {
        if (showsLogo) {
            Image(painterResource(R.drawable.seplis_logo), "SEPLIS", Modifier.size(64.dp).clip(CircleShape))
            Spacer(Modifier.height(20.dp))
        }
        Column(
            Modifier.widthIn(max = if (showsLogo) 442.dp else 382.dp).fillMaxWidth()
                .then(if (showsLogo) Modifier
                    .background(Color(0xFF111111), RoundedCornerShape(16.dp))
                    .border(1.dp, Color.White.copy(alpha = 0.08f), RoundedCornerShape(16.dp))
                    .padding(start = 30.dp, top = 20.dp, end = 30.dp, bottom = 30.dp)
                else Modifier),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text("Sign in to SEPLIS", fontSize = 24.sp, fontWeight = FontWeight.SemiBold,
                modifier = Modifier.widthIn(max = 382.dp).fillMaxWidth().semantics { heading() })
            Spacer(Modifier.height(20.dp))
            if (authorization == null && error == null) {
                Box(Modifier.height(150.dp), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(
                        Modifier.size(16.dp).semantics { contentDescription = "Getting a sign-in code" },
                        color = Color.White, strokeWidth = 2.dp)
                }
            }
            authorization?.takeUnless { model.expired }?.let { current ->
                Row(Modifier.widthIn(max = 382.dp).height(150.dp), verticalAlignment = Alignment.Top,
                    horizontalArrangement = Arrangement.spacedBy(32.dp)) {
                    QRCodeView(current.verificationUriComplete, Modifier.size(150.dp))
                    Column(Modifier.weight(1f).fillMaxHeight(), verticalArrangement = Arrangement.SpaceBetween) {
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text("Go to", color = LibraryStyle.muted, fontSize = 15.sp)
                            Text(current.verificationUri.removePrefix("https://").removePrefix("http://"), fontSize = 20.sp)
                        }
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text("Enter code", color = LibraryStyle.muted, fontSize = 15.sp)
                            Text(current.userCode, fontSize = 48.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace,
                                color = androidx.compose.ui.graphics.Color.White, maxLines = 1,
                                modifier = Modifier.clearAndSetSemantics { contentDescription = "Sign-in code ${current.userCode}" })
                        }
                    }
                }
            }
            error?.let {
                Spacer(Modifier.height(22.dp))
                Text(it, color = LibraryStyle.muted, fontSize = 14.sp, textAlign = TextAlign.Center,
                    modifier = Modifier.widthIn(max = 600.dp).padding(horizontal = 30.dp))
                Spacer(Modifier.height(12.dp))
                TvButton(if (model.expired) "Get New Code" else "Retry", { attempt++ })
            }
            if (onBack != null || session.profiles.isNotEmpty()) {
                Spacer(Modifier.height(18.dp))
                TvButton("Back to accounts", back)
            }
        }
    }
}
