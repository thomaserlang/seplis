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
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
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
fun FilterRangeView(label: String, minimum: String, maximum: String,
    onMinimum: (String) -> Unit, onMaximum: (String) -> Unit) {
    Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
        NumericField("Minimum", minimum, onMinimum, Modifier.weight(1f))
        NumericField("Maximum", maximum, onMaximum, Modifier.weight(1f))
    }
}

@Composable
private fun NumericField(label: String, value: String, onChange: (String) -> Unit, modifier: Modifier) {
    var focused by remember { mutableStateOf(false) }
    Column(modifier, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(label, color = Palette.muted, fontSize = 13.sp)
        BasicTextField(value, onChange,
            modifier = Modifier.fillMaxWidth().height(30.dp).onFocusChanged { focused = it.isFocused }
                .background(Palette.surface, RoundedCornerShape(4.dp))
                .border(1.5.dp, if (focused) Color.White else Color.Transparent, RoundedCornerShape(4.dp))
                .padding(horizontal = 10.dp, vertical = 6.dp),
            singleLine = true, textStyle = TextStyle(color = Color.White, fontSize = 14.sp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            decorationBox = { field -> if (value.isBlank()) Text("Any", color = Palette.muted); field() })
        TvButton("Clear ${label.lowercase()}", { onChange("") }, enabled = value.isNotEmpty(), icon = Icons.Default.Close)
    }
}
