package net.seplis.tv.features.series

import net.seplis.tv.features.library.MediaFactFormat
import net.seplis.tv.features.library.MediaDetailFact

internal fun Series.detailFacts(): List<MediaDetailFact> = buildList {
    year?.let { year -> add(MediaDetailFact("Year", if (endedYear != null && endedYear != year)
        "$year-${endedYear}" else year)) }
    status?.let { listOf("Unknown", "Returning", "Ended", "Cancelled", "In production", "Planned")
        .getOrNull(it)?.takeUnless { value -> value == "Unknown" }?.let { value -> add(MediaDetailFact("Status", value)) } }
    runtime?.takeIf { it > 0 }?.let { add(MediaDetailFact("Runtime", "$it min")) }
    language?.let { add(MediaDetailFact("Language", MediaFactFormat.language(it))) }
    rating?.let { add(MediaDetailFact("IMDb", MediaFactFormat.rating(it))) }
    if (seasons.isNotEmpty()) add(MediaDetailFact(if (seasons.size == 1) "Season" else "Seasons", seasons.size.toString()))
    totalEpisodes?.takeIf { it > 0 }?.let { add(MediaDetailFact("Episodes", it.toString())) }
}
