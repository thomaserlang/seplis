package net.seplis.tv.core.networking

import kotlinx.coroutines.suspendCancellableCoroutine
import okhttp3.Call
import okhttp3.Callback
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import java.io.IOException
import java.util.concurrent.TimeUnit

internal data class HttpResponse(val status: Int, val body: String)

internal object HttpClient {
    private val client = OkHttpClient()

    suspend fun request(request: Request, timeoutMs: Long = 30_000): HttpResponse =
        client.newBuilder().callTimeout(timeoutMs, TimeUnit.MILLISECONDS)
            .connectTimeout(timeoutMs, TimeUnit.MILLISECONDS)
            .readTimeout(timeoutMs, TimeUnit.MILLISECONDS)
            .build().newCall(request).awaitResponse()
}

internal suspend fun Call.awaitResponse(): HttpResponse = suspendCancellableCoroutine { continuation ->
    continuation.invokeOnCancellation { cancel() }
    enqueue(object : Callback {
        override fun onFailure(call: Call, e: IOException) {
            continuation.resumeWith(Result.failure(e))
        }

        override fun onResponse(call: Call, response: Response) {
            val result = runCatching {
                response.use { HttpResponse(it.code, it.body?.string().orEmpty()) }
            }
            continuation.resumeWith(result)
        }
    })
}
