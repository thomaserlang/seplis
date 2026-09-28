package net.seplis.tv.features.cast

import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.core.networking.arrayOrEmpty
import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.objects
import net.seplis.tv.core.networking.page
import net.seplis.tv.core.networking.text
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.Poster

data class CastMember(val id: Int, val name: String, val portrait: Poster?, val roles: List<String>)

class CastRepository(private val api: ApiClient) {
    suspend fun cast(ref: MediaReference, cursor: String? = null) = api.objectAt("${ref.path}/cast",
        mapOf("per_page" to "25") + (cursor?.let { mapOf("cursor" to it) } ?: emptyMap()))
        .page { json ->
            val person = json.getJSONObject("person")
            val roles = json.text("character")?.let(::listOf) ?: json.arrayOrEmpty("roles")
                .objects().mapNotNull { it.text("character") }
            CastMember(person.getInt("id"), person.text("name") ?: "", person.objectOrNull("profile_image")
                ?.text("url")?.let(::Poster), roles)
        }
}
