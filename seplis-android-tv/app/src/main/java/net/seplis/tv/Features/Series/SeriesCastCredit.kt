package net.seplis.tv.features.series

import net.seplis.tv.core.networking.arrayOrEmpty
import net.seplis.tv.core.networking.objects
import net.seplis.tv.core.networking.text
import net.seplis.tv.features.cast.CastMember
import net.seplis.tv.features.cast.CastPerson
import org.json.JSONObject

data class SeriesCastCredit(val person: CastPerson, val roles: List<String>) {
    val member get() = CastMember(person, roles)

    companion object {
        fun from(json: JSONObject) = SeriesCastCredit(CastPerson.from(json.getJSONObject("person")),
            json.arrayOrEmpty("roles").objects().mapNotNull { it.text("character")?.takeIf(String::isNotEmpty) })
    }
}
