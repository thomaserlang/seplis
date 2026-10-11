package net.seplis.tv.features.authentication

import org.json.JSONObject
import java.time.Instant

data class DeviceAuthorization(
    val deviceCode: String, val userCode: String, val verificationUri: String,
    val verificationUriComplete: String,
    val expiresAt: Instant, val pollIntervalSeconds: Long,
) {
    companion object {
        fun from(json: JSONObject) = DeviceAuthorization(
            json.getString("device_code"), json.getString("user_code"), json.getString("verification_uri"),
            json.getString("verification_uri_complete"),
            Instant.parse(json.getString("expires_at")), json.optLong("poll_interval_seconds", 5).coerceAtLeast(1),
        )
    }
}
