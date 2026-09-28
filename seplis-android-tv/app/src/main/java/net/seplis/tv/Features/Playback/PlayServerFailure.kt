package net.seplis.tv.features.playback

import java.io.IOException
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import javax.net.ssl.SSLException
import net.seplis.tv.core.networking.ApiException
import org.json.JSONException

class PlayServerFailure(val statusCode: Int?, message: String = statusCode?.let(ApiException::messageFor)
    ?: "The network request failed.", cause: Throwable? = null) : Exception(message, cause) {
    companion object {
        fun message(error: Throwable): String = when (error) {
            is JSONException -> "The source response has an invalid or missing field."
            is SocketTimeoutException -> "The source request timed out."
            is UnknownHostException -> "The server address could not be resolved."
            is ConnectException -> "A connection to the server could not be established."
            is SSLException -> "The server's HTTPS connection or certificate could not be verified."
            is PlayServerFailure -> error.statusCode?.let { "The source request returned HTTP $it." }
                ?: error.message ?: "The network request failed."
            is IOException -> "The network request failed."
            else -> "The source request failed."
        }
    }
}
