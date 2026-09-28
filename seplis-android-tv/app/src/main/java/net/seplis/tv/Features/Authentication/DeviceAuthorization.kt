package net.seplis.tv.features.authentication

import kotlinx.coroutines.delay
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.core.networking.text
import org.json.JSONObject
import java.time.Instant

data class DeviceAuthorization(
    val deviceCode: String, val userCode: String, val verificationUri: String,
    val expiresAt: Instant, val pollIntervalSeconds: Long,
) {
    companion object {
        fun from(json: JSONObject) = DeviceAuthorization(
            json.getString("device_code"), json.getString("user_code"), json.getString("verification_uri"),
            Instant.parse(json.getString("expires_at")), json.optLong("poll_interval_seconds", 5).coerceAtLeast(1),
        )
    }
}

class DeviceAuthorizationClient(private val api: ApiClient = ApiClient()) {
    suspend fun start(): DeviceAuthorization = DeviceAuthorization.from(api.send("device-authorization", "POST"))

    suspend fun awaitToken(authorization: DeviceAuthorization): String {
        while (Instant.now().isBefore(authorization.expiresAt)) {
            delay(authorization.pollIntervalSeconds * 1_000)
            val response = api.send("device-authorization/token", "POST",
                JSONObject().put("device_code", authorization.deviceCode))
            when (response.text("status")) {
                "authorized" -> return response.text("access_token") ?: error("Approval returned no token")
                "pending" -> Unit
                else -> error("Device sign-in could not be completed")
            }
        }
        error("This code has expired. Request a new code.")
    }
}
