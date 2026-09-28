package net.seplis.tv.features.library

import net.seplis.tv.features.library.MediaKind

enum class CatalogChoice(val queryValue: String?) { ANY(null), YES("true"), NO("false") }

data class CatalogGenre(val id: Int, val name: String)

data class CatalogFilters(
    val sort: String = "popularity_desc", val available: CatalogChoice = CatalogChoice.YES,
    val watched: CatalogChoice = CatalogChoice.ANY, val watchlist: CatalogChoice = CatalogChoice.ANY,
    val favorites: CatalogChoice = CatalogChoice.ANY, val genres: Map<Int, CatalogChoice> = emptyMap(),
    val languages: Set<String> = emptySet(), val yearFrom: String = "", val yearTo: String = "",
    val ratingFrom: String = "", val ratingTo: String = "", val votesFrom: String = "", val votesTo: String = "",
) {
    fun query(kind: MediaKind, cursor: String? = null): List<Pair<String, String>> = buildList {
        add("sort" to sort)
        add("per_page" to "48")
        listOf("user_can_watch" to available, "user_has_watched" to watched,
            "user_watchlist" to watchlist, "user_favorites" to favorites).forEach { (key, value) ->
            value.queryValue?.let { add(key to it) }
        }
        genres.toSortedMap().forEach { (id, choice) ->
            if (choice != CatalogChoice.ANY) add((if (choice == CatalogChoice.YES) "genre_id" else "not_genre_id") to id.toString())
        }
        languages.sorted().forEach { add("language" to it) }
        val date = if (kind == MediaKind.MOVIE) "release_date" else "premiered"
        yearFrom.toIntOrNull()?.let { add("${date}_gt" to "$it-01-01") }
        yearTo.toIntOrNull()?.let { add("${date}_lt" to "$it-12-31") }
        listOf("rating_gt" to ratingFrom, "rating_lt" to ratingTo,
            "rating_votes_gt" to votesFrom, "rating_votes_lt" to votesTo).forEach { (key, value) ->
            if (value.isNotBlank()) add(key to value)
        }
        cursor?.let { add("cursor" to it) }
    }

    val validationError: String? get() {
        for (check in listOf(
            RangeCheck("Year", yearFrom, yearTo, 1800.0..2200.0),
            RangeCheck("Rating", ratingFrom, ratingTo, 0.0..10.0),
            RangeCheck("Votes", votesFrom, votesTo, 0.0..1_000_000_000.0),
        )) {
            val values = listOf(check.lower, check.upper).filter(String::isNotEmpty).map { it.toDoubleOrNull() }
            if (values.any { it == null || it !in check.range || (check.name != "Rating" && it % 1.0 != 0.0) })
                return "Enter a valid ${check.name.lowercase()} value."
            if ((check.lower.toDoubleOrNull() ?: 0.0) > (check.upper.toDoubleOrNull() ?: Double.MAX_VALUE))
                return "${check.name}: minimum must not exceed maximum."
        }
        return null
    }

    companion object {
        fun newSort(kind: MediaKind) = if (kind == MediaKind.MOVIE) "release_date_desc" else "premiered_desc"
        fun sorts(kind: MediaKind) = listOf(
            "Popular" to "popularity_desc", "Newest" to newSort(kind),
            "Oldest" to newSort(kind).replace("_desc", "_asc"), "Top Rated" to "rating_desc",
            "Recently Added" to "user_play_server_${kind.name.lowercase()}_added_desc",
            "Recently Watched" to if (kind == MediaKind.MOVIE) "user_last_watched_at_desc" else "user_last_episode_watched_at_desc",
            "Watchlist Added" to "user_watchlist_added_at_desc", "Favorites Added" to "user_favorite_added_at_desc",
        )
    }
}

private data class RangeCheck(val name: String, val lower: String, val upper: String, val range: ClosedFloatingPointRange<Double>)
