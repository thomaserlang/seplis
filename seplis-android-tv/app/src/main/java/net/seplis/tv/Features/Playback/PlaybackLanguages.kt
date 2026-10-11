package net.seplis.tv.features.playback

import java.util.Locale

object PlaybackLanguages {
    private fun preferred(): List<String> {
        val locales = android.os.LocaleList.getDefault()
        return (0 until locales.size()).map { locales[it].toLanguageTag() }
    }
    fun matches(first: String, second: String): Boolean {
        fun normalized(value: String): String {
            val code = value.lowercase().substringBefore('-').substringBefore('_')
            return runCatching { Locale.forLanguageTag(code).isO3Language }.getOrDefault(code)
        }
        return normalized(first) == normalized(second)
    }

    fun audio(source: PlaySource, saved: String?): PlayStream? {
        match(source.audio, saved)?.let { return it }
        val preferred = listOf("jpn", "eng") + preferred()
        return preferred.firstNotNullOfOrNull { language -> source.audio.firstOrNull { matches(it.language, language) } }
            ?: source.audio.firstOrNull()
    }

    fun subtitle(source: PlaySource, saved: String?, audio: PlayStream?): PlayStream? {
        match(source.subtitles, saved)?.let { return it }
        val preferred = preferred() + "eng"
        val found = preferred.firstNotNullOfOrNull { language -> source.subtitles.firstOrNull { matches(it.language, language) } }
        return if (saved == null && found != null && audio != null && matches(found.language, audio.language)) null else found
            ?: source.subtitles.firstOrNull { it.forced && audio != null && matches(it.language, audio.language) }
    }

    private fun match(streams: List<PlayStream>, key: String?): PlayStream? = key?.let {
        streams.firstOrNull { stream -> stream.key == it }
            ?: streams.firstOrNull { stream -> matches(stream.language, it.substringBefore(':')) }
    }
}
