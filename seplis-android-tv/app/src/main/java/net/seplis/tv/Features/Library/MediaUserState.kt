package net.seplis.tv.features.library

import org.json.JSONObject
import net.seplis.tv.core.networking.flag
import net.seplis.tv.core.networking.integer
import net.seplis.tv.core.networking.objectOrNull
import net.seplis.tv.core.networking.text

data class Watched(val times: Int = 0, val position: Int = 0) {
    companion object {
        fun from(json: JSONObject?): Watched = Watched(json?.optInt("times") ?: 0, json?.optInt("position") ?: 0)
    }
}
