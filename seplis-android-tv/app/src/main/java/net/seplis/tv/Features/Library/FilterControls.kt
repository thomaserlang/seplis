package net.seplis.tv.features.library

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.width
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.TvButton

@Composable
fun FilterChoiceRow(label: String, choice: CatalogChoice, inclusiveLabels: Boolean = false,
    onChange: (CatalogChoice) -> Unit) {
    Row(horizontalArrangement = Arrangement.spacedBy(4.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(label, modifier = Modifier.weight(1f), fontSize = 12.sp)
        CatalogChoice.entries.forEach { value ->
            val text = when (value) {
                CatalogChoice.ANY -> "Any"
                CatalogChoice.YES -> if (inclusiveLabels) "Include" else "Yes"
                CatalogChoice.NO -> if (inclusiveLabels) "Exclude" else "No"
            }
            TvButton(text, { onChange(value) }, Modifier.width(65.dp), selected = choice == value, color = LibraryStyle.filterSelected,
                accessibilityLabel = "$label: $text")
        }
    }
}
