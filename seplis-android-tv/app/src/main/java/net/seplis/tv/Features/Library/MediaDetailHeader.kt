package net.seplis.tv.features.library

import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Icon
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.text
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import net.seplis.tv.components.LibraryStyle

@Composable
fun MediaDetailHeader(media: MediaDetailInfo) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
            val title = media.title
            val originalTitle = media.originalTitle
            val tagline = media.tagline
            Text(title, fontSize = 21.sp, lineHeight = 25.sp, fontWeight = FontWeight.SemiBold)
            if (!originalTitle.isNullOrBlank() && originalTitle != title) {
                Text(originalTitle, fontSize = 10.5.sp, lineHeight = 13.sp, color = LibraryStyle.muted)
            }
            if (!tagline.isNullOrBlank()) {
                Text(tagline, fontSize = 10.5.sp, lineHeight = 13.sp,
                    fontStyle = FontStyle.Italic, color = LibraryStyle.muted)
            }
        }
        if (media.detailFacts.isNotEmpty()) Row(horizontalArrangement = Arrangement.spacedBy(15.dp)) {
            media.detailFacts.forEach { (label, value) ->
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(label.uppercase(), fontSize = 8.sp, lineHeight = 10.sp,
                        fontWeight = FontWeight.SemiBold, color = LibraryStyle.muted)
                    val rating = label == "IMDb"
                    val color = if (rating) Color(0xFFFFCC00) else Color.White
                    // Android's fallback star glyph changes the line metrics; an icon keeps facts aligned.
                    Row(verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(3.dp),
                        modifier = Modifier.clearAndSetSemantics { text = AnnotatedString(value) }) {
                        if (rating) Icon(Icons.Default.Star, contentDescription = null,
                            tint = color, modifier = Modifier.size(10.5.dp))
                        Text(if (rating) value.removePrefix("★ ") else value,
                            fontSize = 10.5.sp, lineHeight = 13.sp, fontWeight = FontWeight.SemiBold,
                            color = color)
                    }
                }
            }
        }
    }
}

@Composable
fun MediaDetailDescription(media: MediaDetailInfo) {
    val genres = media.genres
    val plot = media.plot
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        if (genres.isNotEmpty()) Text(genres.joinToString(" · "), color = LibraryStyle.muted,
            fontSize = 11.sp, lineHeight = 14.sp)
        if (!plot.isNullOrBlank()) Text(plot, color = LibraryStyle.muted,
            style = TextStyle(fontSize = 12.sp, lineHeight = 15.sp, letterSpacing = 0.sp),
            maxLines = 5, overflow = TextOverflow.Ellipsis)
    }
}
