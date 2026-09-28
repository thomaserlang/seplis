package net.seplis.tv.features.authentication

import androidx.compose.foundation.Image
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.Row
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import androidx.lifecycle.repeatOnLifecycle
import kotlinx.coroutines.CancellationException
import net.seplis.tv.R
import net.seplis.tv.app.AppSession
import net.seplis.tv.components.Palette
import net.seplis.tv.components.TvButton

@Composable
fun DeviceLoginView(session: AppSession, onBack: (() -> Unit)? = null, onSignedIn: () -> Unit = {}) {
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

    Column(Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center) {
        Image(painterResource(R.drawable.seplis_logo), "SEPLIS", Modifier.size(48.dp).clip(CircleShape))
        Spacer(Modifier.height(20.dp))
        if (authorization == null && error == null) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                CircularProgressIndicator(Modifier.size(16.dp), color = androidx.compose.ui.graphics.Color.White, strokeWidth = 2.dp)
                Text("Getting a sign-in code", color = Palette.muted, fontSize = 14.sp)
            }
        }
        authorization?.takeUnless { model.expired }?.let { current ->
            Text("Go to", color = Palette.muted, fontSize = 15.sp)
            Spacer(Modifier.height(6.dp))
            Text(current.verificationUri.removePrefix("https://").removePrefix("http://"), fontSize = 20.sp)
            Spacer(Modifier.height(20.dp))
            Text("Enter code", color = Palette.muted, fontSize = 15.sp)
            Spacer(Modifier.height(6.dp))
            Text(current.userCode, fontSize = 38.sp, fontWeight = FontWeight.SemiBold, fontFamily = FontFamily.Monospace,
                modifier = Modifier.clearAndSetSemantics { contentDescription = "Sign-in code ${current.userCode}" })
        }
        error?.let {
            Spacer(Modifier.height(22.dp))
            Text(it, color = Palette.muted, fontSize = 14.sp, textAlign = TextAlign.Center,
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
