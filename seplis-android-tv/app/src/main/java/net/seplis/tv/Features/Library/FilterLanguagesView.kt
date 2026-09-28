package net.seplis.tv.features.library

import androidx.compose.foundation.border
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CheckboxDefaults
import net.seplis.tv.components.Palette
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import java.util.Locale

@Composable
fun FilterLanguagesView(selection: Set<String>, onChange: (Set<String>) -> Unit) {
    val languages = remember { Locale.getISOLanguages().map { code ->
        Locale.forLanguageTag(code).getDisplayLanguage(Locale.getDefault()) to code
    }.sortedBy { it.first } }
    languages.forEach { (name, code) ->
        var focused by remember(code) { mutableStateOf(false) }
        Row(Modifier.fillMaxWidth().height(30.dp)
            .background(if (code in selection) Palette.filterSelected else Palette.surface, RoundedCornerShape(4.dp))
            .border(1.5.dp, if (focused) Color.White else Color.Transparent, RoundedCornerShape(4.dp))
            .onFocusChanged { focused = it.isFocused }
            .toggleable(code in selection, role = Role.Checkbox) { selected ->
                onChange(if (selected) selection + code else selection - code)
            }.padding(horizontal = 12.dp), verticalAlignment = Alignment.CenterVertically) {
            Text(name, Modifier.weight(1f), fontSize = 13.sp)
            Checkbox(code in selection, onCheckedChange = null, modifier = Modifier.size(24.dp),
                colors = CheckboxDefaults.colors(checkedColor = Color.White, uncheckedColor = Color.White, checkmarkColor = Palette.filterSelected))
        }
    }
}
