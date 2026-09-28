package net.seplis.tv.features.library

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.CancellationException
import net.seplis.tv.components.MessagePanel
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.tv.material3.Text
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.components.Palette
import net.seplis.tv.components.TvButton
import java.util.Locale

@Composable
fun FilterChoiceRow(label: String, choice: FilterChoice, inclusiveLabels: Boolean = false,
    onChange: (FilterChoice) -> Unit) {
    Row(horizontalArrangement = Arrangement.spacedBy(4.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(label, modifier = Modifier.weight(1f), fontSize = 12.sp)
        FilterChoice.entries.forEach { value ->
            val text = when (value) {
                FilterChoice.ANY -> "Any"
                FilterChoice.YES -> if (inclusiveLabels) "Include" else "Yes"
                FilterChoice.NO -> if (inclusiveLabels) "Exclude" else "No"
            }
            TvButton(text, { onChange(value) }, Modifier.width(65.dp), selected = choice == value, color = Palette.filterSelected,
                accessibilityLabel = "$label: $text")
        }
    }
}
