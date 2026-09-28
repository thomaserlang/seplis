package net.seplis.tv.features.authentication

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.CancellationException
import net.seplis.tv.app.AppSession
import net.seplis.tv.core.networking.ApiException
import java.time.Instant

class DeviceLoginModel(private val session: AppSession) {
    private val client = DeviceAuthorizationClient(session.authorizationAPI)
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
                    authorization = client.start()
                    expired = false
                }
                receivedToken = client.awaitToken(requireNotNull(authorization))
            }
            session.signIn(requireNotNull(receivedToken))
            return true
        } catch (cancelled: CancellationException) { throw cancelled }
        catch (failure: Exception) {
            if (failure is ApiException && failure.status == 401) receivedToken = null
            expired = (failure is ApiException && failure.status in listOf(401, 404, 410)) ||
                authorization?.expiresAt?.isAfter(Instant.now()) == false
            error = failure.message ?: "Could not sign in"
            return false
        }
    }
}
