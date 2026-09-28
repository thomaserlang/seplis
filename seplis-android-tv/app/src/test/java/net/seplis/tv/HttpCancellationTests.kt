package net.seplis.tv

import kotlinx.coroutines.*
import net.seplis.tv.core.networking.awaitResponse
import okhttp3.*
import okio.Timeout
import java.io.IOException
import org.junit.Assert.*
import org.junit.Test

class HttpCancellationTests {
    private class PendingCall : Call {
        val started = CompletableDeferred<Unit>()
        private var cancelled = false
        private var callback: Callback? = null
        override fun request() = Request.Builder().url("https://example.test").build()
        override fun enqueue(responseCallback: Callback) { callback = responseCallback; started.complete(Unit) }
        override fun execute(): Response = error("Only asynchronous calls are supported")
        override fun cancel() { cancelled = true; callback?.onFailure(this, IOException("Cancelled")) }
        override fun isExecuted() = started.isCompleted
        override fun isCanceled() = cancelled
        override fun timeout() = Timeout.NONE
        override fun clone(): Call = PendingCall()
    }

    @Test fun cancellationAbortsTheCallWithoutWaitingForItsResponse() = runBlocking {
        val call = PendingCall()
        val request = launch { call.awaitResponse() }
        call.started.await()
        withTimeout(1_000) { request.cancelAndJoin() }
        assertTrue(call.isCanceled())
        assertTrue(request.isCancelled)
    }
}
