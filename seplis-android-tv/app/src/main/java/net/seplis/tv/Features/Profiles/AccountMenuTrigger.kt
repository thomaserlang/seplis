package net.seplis.tv.features.profiles

import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import net.seplis.tv.components.TvButton

@Composable
fun AccountMenuTrigger(accountName: String, focusChanged: (Boolean) -> Unit,
    open: () -> Unit, modifier: Modifier = Modifier) {
    TvButton(accountName, open, modifier.width(130.dp), flat = true,
        icon = Icons.Default.AccountCircle, onFocusChange = focusChanged, alignStart = true)
}
