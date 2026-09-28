package net.seplis.tv

import androidx.compose.ui.test.*
import org.junit.Test

class CatalogFilterUITests : UITestCase() {
    @Test fun yearMinimumCanBeSetAndCleared() {
        awaitText("Alex")
        compose.onNodeWithText("Movies").performClick()
        awaitText("Filters")
        compose.onNodeWithText("Filters").performClick()
        compose.onNodeWithText("Year").performClick()
        compose.onNodeWithText("Clear minimum").assertIsNotEnabled()
        compose.onAllNodes(hasSetTextAction()).onFirst().performTextInput("2000")
        compose.onNodeWithText("Clear minimum").assertIsEnabled().performClick()
        compose.onNodeWithText("Clear minimum").assertIsNotEnabled()
        compose.onNodeWithContentDescription("Cancel").performClick()
        compose.onNodeWithText("Filters").assertIsDisplayed()
    }
}
