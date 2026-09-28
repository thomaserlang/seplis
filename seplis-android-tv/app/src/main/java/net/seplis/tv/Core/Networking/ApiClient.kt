package net.seplis.tv.core.networking

import android.net.Uri
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import okhttp3.Request
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody

fun interface ApiTransport {
    suspend fun request(path: String, method: String, query: List<Pair<String, String>>, body: JSONObject?): String
}

class ApiClient(private val token: String? = null, private val transport: ApiTransport? = null) {
    var onUnauthorized: (() -> Unit)? = null
    companion object { const val BASE = "https://api.seplis.net/2/" }

    suspend fun objectAt(path: String, query: Map<String, String> = emptyMap()): JSONObject =
        objectAt(path, query.map { it.key to it.value })

    suspend fun objectAt(path: String, query: List<Pair<String, String>>): JSONObject =
        JSONObject(request(path, query = query).ifEmpty { "{}" })

    suspend fun optionalObject(path: String): JSONObject? =
        request(path).takeIf { it.isNotBlank() && it != "null" }?.let(::JSONObject)

    suspend fun arrayAt(path: String, query: Map<String, String> = emptyMap()): JSONArray =
        JSONArray(request(path, query = query.map { it.key to it.value }))

    suspend fun send(path: String, method: String, body: JSONObject? = null): JSONObject =
        JSONObject(request(path, method = method, body = body).ifEmpty { "{}" })

    suspend fun perform(path: String, method: String, body: JSONObject? = null) {
        request(path, method = method, body = body)
    }

    private suspend fun request(
        path: String, method: String = "GET", query: List<Pair<String, String>> = emptyList(), body: JSONObject? = null,
    ): String = withContext(Dispatchers.IO) {
        transport?.let {
            try { return@withContext it.request(path, method, query, body) }
            catch (failure: ApiException) {
                if (failure.status == 401 && token != null) withContext(Dispatchers.Main) { onUnauthorized?.invoke() }
                throw failure
            }
        }
        check(!net.seplis.tv.BuildConfig.USE_FIXTURES) { "Fixture builds cannot use the live API" }
        val builder = Uri.parse(BASE + path.trimStart('/')).buildUpon()
        query.forEach { (key, value) -> builder.appendQueryParameter(key, value) }
        val payload = when {
            body != null -> body.toString().toRequestBody("application/json".toMediaType())
            method in listOf("POST", "PUT", "PATCH") -> ByteArray(0).toRequestBody()
            else -> null
        }
        val request = Request.Builder().url(builder.build().toString()).method(method, payload)
            .header("Accept", "application/json")
        token?.let { request.header("Authorization", "Bearer $it") }
        val response = HttpClient.request(request.build())
        if (response.status !in 200..299) {
            if (response.status == 401 && token != null) withContext(Dispatchers.Main) { onUnauthorized?.invoke() }
            throw ApiException(response.status)
        }
        response.body
    }

}
