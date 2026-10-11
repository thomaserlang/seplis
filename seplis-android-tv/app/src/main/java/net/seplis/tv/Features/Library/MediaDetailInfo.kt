package net.seplis.tv.features.library

import java.text.NumberFormat
import java.util.Locale

data class MediaDetailFact(val label: String, val value: String)

interface MediaDetailInfo {
    val title: String
    val originalTitle: String?
    val tagline: String?
    val plot: String?
    val genres: List<String>
    val detailFacts: List<MediaDetailFact>
}

object MediaFactFormat {
    fun money(value: Long): String = when {
        value >= 1_000_000_000 -> "$${String.format(Locale.US, "%.1f", value / 1_000_000_000.0)}B"
        value >= 1_000_000 -> "$${String.format(Locale.US, "%.0f", value / 1_000_000.0)}M"
        else -> "$${NumberFormat.getIntegerInstance().format(value)}"
    }

    fun language(code: String): String = Locale.forLanguageTag(code).getDisplayLanguage(Locale.ENGLISH).ifBlank { code }
    fun rating(value: Double): String = String.format(Locale.US, "★ %.1f", value)
}
