package net.seplis.tv

import net.seplis.tv.features.library.CatalogFilters
import net.seplis.tv.features.library.FilterChoice
import net.seplis.tv.features.library.MediaKind
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class CatalogFiltersTest {
    @Test fun repeatedGenreAndLanguageParametersArePreserved() {
        val query = CatalogFilters(genres = mapOf(1 to FilterChoice.YES, 2 to FilterChoice.NO),
            languages = setOf("en", "da")).query(MediaKind.SERIES)
        assertEquals(listOf("1"), query.filter { it.first == "genre_id" }.map { it.second })
        assertEquals(listOf("2"), query.filter { it.first == "not_genre_id" }.map { it.second })
        assertEquals(listOf("da", "en"), query.filter { it.first == "language" }.map { it.second })
    }

    @Test fun invalidRangesCannotBeApplied() {
        assertEquals("Year: minimum must not exceed maximum.",
            CatalogFilters(yearFrom = "2026", yearTo = "2020").validationError)
        assertNull(CatalogFilters(ratingFrom = "7.5", ratingTo = "9").validationError)
    }
}
