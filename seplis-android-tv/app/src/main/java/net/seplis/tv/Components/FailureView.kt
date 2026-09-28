package net.seplis.tv.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text

@Composable
fun FailureView(message: String, retry: (() -> Unit)? = null, modifier: Modifier = Modifier) {
    Column(modifier.padding(24.dp), horizontalAlignment = Alignment.Start) {
        Text(message, fontSize = 14.sp, color = LibraryStyle.muted)
        if (retry != null) {
            Spacer(Modifier.height(14.dp))
            TvButton("Retry", retry)
        }
    }
}
