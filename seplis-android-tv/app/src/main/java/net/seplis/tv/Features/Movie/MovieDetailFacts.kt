package net.seplis.tv.features.movie

import net.seplis.tv.features.library.MediaFactFormat
import net.seplis.tv.features.library.MediaDetailFact

internal fun Movie.detailFacts(): List<MediaDetailFact> = buildList {
    year?.let { add(MediaDetailFact("Year", it)) }
    status?.let { listOf("Unknown", "Released", "In production", "Planned", "Cancelled", "Rumored")
        .getOrNull(it)?.takeUnless { value -> value == "Unknown" }?.let { value -> add(MediaDetailFact("Status", value)) } }
    runtime?.takeIf { it > 0 }?.let {
        add(MediaDetailFact("Runtime", if (it < 60) "${it}m" else if (it % 60 == 0) "${it / 60}h" else "${it / 60}h ${it % 60}m"))
    }
    language?.let { add(MediaDetailFact("Language", MediaFactFormat.language(it))) }
    rating?.let { add(MediaDetailFact("IMDb", MediaFactFormat.rating(it))) }
    budget?.takeIf { it > 0 }?.let { add(MediaDetailFact("Budget", MediaFactFormat.money(it))) }
    revenue?.takeIf { it > 0 }?.let { add(MediaDetailFact("Revenue", MediaFactFormat.money(it))) }
}
