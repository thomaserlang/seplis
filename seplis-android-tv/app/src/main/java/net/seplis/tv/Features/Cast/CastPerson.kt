package net.seplis.tv.features.cast

import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.text
import net.seplis.tv.features.library.Poster
import org.json.JSONObject

data class CastPerson(val id: Int, val name: String, val profileImage: Poster?) {
    companion object {
        fun from(json: JSONObject) = CastPerson(json.getInt("id"), json.text("name") ?: "",
            json.objectOrNull("profile_image")?.text("url")?.let(::Poster))
    }
}

data class CastMember(val person: CastPerson, val roles: List<String>) {
    val id get() = person.id
}
