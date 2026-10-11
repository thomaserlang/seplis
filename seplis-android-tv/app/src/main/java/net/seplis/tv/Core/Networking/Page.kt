package net.seplis.tv.core.networking

import org.json.JSONObject

data class Page<T>(val records: List<T>, val cursor: String?)

fun <T> JSONObject.page(parse: (JSONObject) -> T): Page<T> =
    Page(arrayOrEmpty("records").objects().map(parse), text("cursor"))
