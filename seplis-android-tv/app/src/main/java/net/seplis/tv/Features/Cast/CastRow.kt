package net.seplis.tv.features.cast

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.CompositingStrategy
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.focusGroup
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.focusRestorer
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.components.MessagePanel
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import net.seplis.tv.components.Palette

@Composable
fun CastRow(reference: MediaReference, api: ApiClient) {
    val model = remember(reference, api) { CastRowModel(reference, api) }
    val scope = rememberCoroutineScope()
    LaunchedEffect(model) { model.load() }
    val members = model.members
    if (model.hasLoaded && members.isEmpty() && !model.isLoading && model.error == null) return
    var focused by remember { mutableStateOf<CastMember?>(null) }
    val firstPortrait = remember { FocusRequester() }
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Row(Modifier.height(21.dp), horizontalArrangement = Arrangement.spacedBy(9.dp), verticalAlignment = Alignment.CenterVertically) {
            Text("Top Cast", color = Palette.muted, fontSize = 14.sp, fontWeight = FontWeight.Medium,
                modifier = Modifier.alignByBaseline())
            focused?.let { person ->
                Text(person.name, color = if (person.roles.isEmpty()) Color.White else Palette.muted,
                    fontSize = 11.sp, fontWeight = FontWeight.Medium, maxLines = 1,
                    overflow = TextOverflow.Ellipsis, modifier = Modifier.weight(1f, fill = false).alignByBaseline())
                if (person.roles.isNotEmpty()) {
                    Text("·", color = Palette.muted, modifier = Modifier.alignByBaseline())
                    Text(person.roles.joinToString(" / "), fontSize = 10.5.sp, color = Palette.muted,
                        maxLines = 1, overflow = TextOverflow.Ellipsis, modifier = Modifier.weight(1f, fill = false).alignByBaseline())
                }
            }
        }
            LazyRow(Modifier.fillMaxWidth()
                .focusRestorer(if (members.isEmpty()) FocusRequester.Default else firstPortrait).focusGroup()
                .graphicsLayer { compositingStrategy = CompositingStrategy.Offscreen }
                .drawWithContent {
                    drawContent()
                    drawRect(Brush.horizontalGradient(0f to Color.Black, 0.88f to Color.Black, 1f to Color.Transparent),
                        blendMode = BlendMode.DstIn)
                }, contentPadding = PaddingValues(top = 4.dp, bottom = 4.dp, end = 60.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                itemsIndexed(members, key = { _, person -> person.id }) { index, person ->
                    LaunchedEffect(index, members.size) {
                        if (index >= members.size - 5 && model.error == null) scope.launch { model.load(more = true) }
                    }
                    CastPortrait(person, if (index == 0) Modifier.focusRequester(firstPortrait) else Modifier) { hasFocus ->
                        if (hasFocus) focused = person else if (focused?.id == person.id) focused = null
                    }
                }
                if (model.isLoading || !model.hasLoaded && model.error == null) items(8) {
                    net.seplis.tv.components.PosterSkeleton(70.dp)
                }
                model.error?.let { message -> item {
                    MessagePanel(message, retry = { scope.launch { model.load(more = members.isNotEmpty()) } }, modifier = Modifier.width(220.dp))
                } }
            }
    }
}
