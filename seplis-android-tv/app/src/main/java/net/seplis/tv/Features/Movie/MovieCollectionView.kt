package net.seplis.tv.features.movie
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.width
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.focusRestorer
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.components.FailureView
import androidx.compose.runtime.Composable
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.PosterView

@Composable
fun MovieCollectionView(collection: MovieCollection, api: APIClient, currentMovieID: Int,
    onOpen: (MediaReference) -> Unit) {
    val model = remember(collection, api) { MovieCollectionModel(collection, api) }
    val scope = rememberCoroutineScope()
    LaunchedEffect(model) { model.load() }
    val movies = model.movies
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(collection.name, color = LibraryStyle.muted, fontSize = 14.sp)
        LazyRow(modifier = Modifier.focusRestorer(), horizontalArrangement = Arrangement.spacedBy(10.dp), contentPadding = PaddingValues(2.dp)) {
            itemsIndexed(movies, key = { _, item -> item.id }) { index, item ->
                LaunchedEffect(index, movies.size) {
                    if (index >= movies.size - 5 && model.error == null) scope.launch { model.load(more = true) }
                }
                PosterView(item.title, item.poster, { onOpen(MediaReference(MediaKind.MOVIE, item.id)) },
                    width = 92.dp, height = 138.dp, enabled = item.id != currentMovieID)
            }
            if (model.isLoading) item { net.seplis.tv.components.PosterSkeleton() }
            model.error?.let { message -> item {
                FailureView(message, retry = { scope.launch { model.load(more = movies.isNotEmpty()) } }, modifier = Modifier.width(220.dp))
            } }
        }
    }
}
