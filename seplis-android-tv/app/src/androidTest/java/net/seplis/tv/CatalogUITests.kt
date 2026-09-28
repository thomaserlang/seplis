package net.seplis.tv

import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.v2.createComposeRule
import net.seplis.tv.core.networking.*
import net.seplis.tv.features.library.*
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

class CatalogUITests {
    @get:Rule val compose = createComposeRule()

    @Test fun emptyCatalogShowsItsEmptyState() {
        val model = CatalogModel(MediaKind.MOVIE, ApiClient("fixture", ApiTransport { _, _, _, _ ->
            """{"records":[],"cursor":null}"""
        }))
        compose.setContent { CatalogView(MediaKind.MOVIE, model, 0, 0, {}, {}) }
        compose.waitUntil(5_000) { model.hasLoaded }
        compose.onNodeWithText("No titles found").assertIsDisplayed()
    }

    @Test fun paginationFailureIsVisibleAndRetryKeepsExistingTitles() {
        var offline = true
        val model = CatalogModel(MediaKind.MOVIE, ApiClient("fixture", ApiTransport { _, _, query, _ ->
            if (query.any { it.first == "cursor" }) {
                if (offline) throw ApiException(503, "Fixture page unavailable")
                """{"records":[{"id":2,"title":"Second title"}],"cursor":null}"""
            } else """{"records":[{"id":1,"title":"First title"}],"cursor":"next"}"""
        }))
        compose.setContent { CatalogView(MediaKind.MOVIE, model, 0, 0, {}, {}) }
        compose.waitUntil(5_000) { model.hasLoaded }
        compose.onNodeWithContentDescription("First title").performSemanticsAction(SemanticsActions.RequestFocus)
        compose.waitUntil(5_000) { model.error != null }
        compose.onNode(hasScrollToIndexAction()).performScrollToIndex(1)
        compose.onNodeWithText("Fixture page unavailable").performScrollTo().assertIsDisplayed()
        offline = false
        compose.onNodeWithText("Retry").performScrollTo().performClick()
        compose.waitUntil(5_000) { model.items.size == 2 }
        assertEquals(listOf(1, 2), model.items.map { it.id })
        assertNull(model.error)
    }

    @Test fun failedFilterChangeDoesNotShowThePreviousResults() {
        val model = CatalogModel(MediaKind.MOVIE, ApiClient("fixture", ApiTransport { _, _, query, _ ->
            if (query.any { it == "sort" to "release_date_desc" }) throw ApiException(503, "Fixture catalog unavailable")
            """{"records":[{"id":1,"title":"Old results"}],"cursor":null}"""
        }))
        compose.setContent { CatalogView(MediaKind.MOVIE, model, 0, 0, {}, {}) }
        compose.waitUntil(5_000) { model.hasLoaded }
        compose.onNodeWithText("New").performClick()
        compose.waitUntil(5_000) { model.error != null }
        compose.onNodeWithText("Fixture catalog unavailable").assertIsDisplayed()
        compose.onNodeWithContentDescription("Old results").assertDoesNotExist()
    }
}
