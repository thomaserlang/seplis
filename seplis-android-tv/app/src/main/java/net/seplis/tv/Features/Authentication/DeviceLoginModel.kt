package net.seplis.tv.features.authentication

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import net.seplis.tv.app.AppSession
import net.seplis.tv.core.networking.APIError
import net.seplis.tv.core.networking.text
import org.json.JSONObject
import java.time.Instant

class DeviceLoginModel(private val session: AppSession) {
    private val api = session.authorizationAPI
    var authorization by mutableStateOf<DeviceAuthorization?>(null)
        private set
    var error by mutableStateOf<String?>(null)
        private set
    var expired by mutableStateOf(false)
        private set
    private var receivedToken: String? = null

    suspend fun run(): Boolean {
        error = null
        try {
            if (receivedToken == null) {
                if (authorization == null || expired) {
                    authorization = DeviceAuthorization.from(api.send("device-authorization", "POST"))
                    expired = false
                }
                val current = requireNotNull(authorization)
                while (Instant.now().isBefore(current.expiresAt)) {
                    delay(2_000)
                    val response = api.send("device-authorization/token", "POST",
                        JSONObject().put("device_code", current.deviceCode))
                    when (response.text("status")) {
                        "authorized" -> {
                            receivedToken = response.text("access_token")?.takeIf { it.isNotEmpty() }
                                ?: error("Approval returned no token")
                            break
                        }
                        "pending" -> Unit
                        else -> error("Device sign-in could not be completed")
                    }
                }
                check(receivedToken != null) { "This code has expired. Request a new code." }
            }
            session.signIn(requireNotNull(receivedToken))
            return true
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) {
            if (failure is APIError && failure.status == 401) receivedToken = null
            expired = (failure is APIError && failure.status in listOf(401, 404, 410)) ||
                authorization?.expiresAt?.isAfter(Instant.now()) == false
            error = failure.message ?: "Could not sign in"
            return false
        }
    }
}
