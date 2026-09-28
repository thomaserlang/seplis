package net.seplis.tv.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.unit.dp

@Composable
fun PosterSkeletonRow() {
    LazyRow(
        modifier = Modifier.clearAndSetSemantics { contentDescription = "Loading titles" },
        userScrollEnabled = false,
        contentPadding = PaddingValues(horizontal = LibraryStyle.horizontalInset, vertical = 5.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        items(10) { PosterSkeleton() }
    }
}
