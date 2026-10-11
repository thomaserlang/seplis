package net.seplis.tv.core.networking

import org.json.JSONArray
import org.json.JSONObject

fun JSONObject.text(key: String): String? =
    if (isNull(key)) null else optString(key).takeIf { it.isNotBlank() }

fun JSONObject.objectOrNull(key: String): JSONObject? = optJSONObject(key)
fun JSONObject.arrayOrEmpty(key: String): JSONArray = optJSONArray(key) ?: JSONArray()
fun JSONArray.objects(): List<JSONObject> = (0 until length()).mapNotNull(::optJSONObject)
fun JSONObject.number(key: String): Double? = when (val value = opt(key)) {
    is Number -> value.toDouble()
    is String -> value.toDoubleOrNull()
    else -> null
}
fun JSONObject.integer(key: String): Int? = number(key)?.toInt()
fun JSONObject.flag(key: String): Boolean? = when (val value = opt(key)) {
    is Boolean -> value
    else -> null
}
