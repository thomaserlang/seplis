package net.seplis.tv.app

import android.os.Bundle
import android.view.WindowInsets
import android.view.WindowInsetsController
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.remember
import net.seplis.tv.components.Palette
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.darkColorScheme
import androidx.tv.material3.LocalContentColor
import androidx.tv.material3.LocalTextStyle
import androidx.compose.ui.unit.sp
import androidx.compose.ui.graphics.Color
import android.content.Intent
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import net.seplis.tv.features.topshelf.TopShelfLink

class MainActivity : ComponentActivity() {
    private var pendingLink by mutableStateOf<TopShelfLink?>(null)
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        pendingLink = TopShelfLink.parse(intent.data)
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        pendingLink = TopShelfLink.parse(intent.data)
        enableEdgeToEdge()
        window.decorView.windowInsetsController?.apply {
            hide(WindowInsets.Type.systemBars())
            systemBarsBehavior = WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
        setContent {
            MaterialTheme(colorScheme = darkColorScheme(
                background = Palette.background, onBackground = Color.White,
                surface = Palette.surface, onSurface = Color.White,
            )) {
                CompositionLocalProvider(
                    LocalContentColor provides Color.White,
                    LocalTextStyle provides MaterialTheme.typography.bodyLarge.copy(letterSpacing = 0.sp),
                ) {
                    AppView(remember { SessionFactory.create(applicationContext) }, pendingLink) {
                        pendingLink = null
                        intent.data = null
                    }
                }
            }
        }
    }
}
