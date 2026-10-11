package net.seplis.tv.core.networking

class APIError(val status: Int, message: String = messageFor(status)) : Exception(message) {
    companion object {
        fun messageFor(status: Int): String = when (status) {
            401 -> "Your session has expired. Sign in again."
            403 -> "You do not have access to this item."
            404 -> "This item is no longer available."
            410 -> "This code has expired. Request a new code."
            429 -> "Too many requests. Please try again shortly."
            else -> "The server could not complete the request ($status)."
        }
    }
}
