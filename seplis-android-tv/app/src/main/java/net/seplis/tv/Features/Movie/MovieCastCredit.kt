package net.seplis.tv.features.movie

import net.seplis.tv.core.networking.text
import net.seplis.tv.features.cast.CastMember
import net.seplis.tv.features.cast.CastPerson
import org.json.JSONObject

data class MovieCastCredit(val person: CastPerson, val character: String?) {
    val member get() = CastMember(person, character?.let(::listOf) ?: emptyList())

    companion object {
        fun from(json: JSONObject) = MovieCastCredit(CastPerson.from(json.getJSONObject("person")), json.text("character"))
    }
}
