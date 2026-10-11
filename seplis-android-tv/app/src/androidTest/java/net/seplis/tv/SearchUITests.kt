package net.seplis.tv

import net.seplis.tv.shared.topshelf.*

import androidx.compose.runtime.*
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.v2.createComposeRule
import kotlinx.coroutines.CompletableDeferred
import net.seplis.tv.core.networking.*
import net.seplis.tv.features.home.*
import net.seplis.tv.features.library.*
import net.seplis.tv.features.search.*
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

class SearchUITests {
    @get:Rule val compose = createComposeRule()

    @Test fun searchDoesNotShowEmptyResultsUntilTheRequestFinishes() {
        val release = CompletableDeferred<Unit>()
        val model = SearchModel(APIClient("fixture", ApiTransport { _, _, _, _ -> release.await(); "[]" }))
        compose.setContent { SearchView(model, 0, 0, {}, {}) }
        compose.onNode(hasSetTextAction()).performTextInput("Fixture")
        compose.waitUntil(5_000) { model.isLoading }
        compose.onNodeWithText("No results for \"Fixture\"").assertDoesNotExist()
        release.complete(Unit)
        compose.waitUntil(5_000) { !model.isLoading }
        compose.onNodeWithText("No results for \"Fixture\"").assertIsDisplayed()
    }
}
