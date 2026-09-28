package net.seplis.tv.features.cast

import androidx.compose.foundation.background
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.foundation.border
import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AccountBox
import androidx.compose.material3.Icon
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.unit.dp
import coil3.compose.AsyncImage
import net.seplis.tv.components.LibraryStyle

@Composable
fun CastPortrait(person: CastPerson, modifier: Modifier = Modifier, onFocus: (Boolean) -> Unit) {
    var selected by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(if (selected) 1.05f else 1f, tween(150), label = "cast focus")
    Box(modifier.width(70.dp).height(105.dp)
        .onFocusChanged { selected = it.isFocused; onFocus(it.isFocused) }
        .focusable()) {
        Box(Modifier.matchParentSize().graphicsLayer {
            scaleX = scale; scaleY = scale; transformOrigin = TransformOrigin(0f, 0.5f)
        }.clip(RoundedCornerShape(4.dp))
            .background(Color(0xFF1F1F1F))
            .border(1.5.dp, if (selected) Color.White else Color.Transparent, RoundedCornerShape(4.dp)),
            contentAlignment = Alignment.Center) {
            Icon(Icons.Outlined.AccountBox, contentDescription = null, tint = LibraryStyle.muted,
                modifier = Modifier.size(24.dp))
            AsyncImage(model = person.profileImage?.thumbnail, contentDescription = null,
                modifier = Modifier.matchParentSize(), contentScale = ContentScale.Crop)
        }
    }
}
