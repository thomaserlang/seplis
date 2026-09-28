package net.seplis.tv

import kotlinx.coroutines.*
import net.seplis.tv.app.*
import net.seplis.tv.core.networking.*
import net.seplis.tv.core.security.*
import net.seplis.tv.features.authentication.DeviceLoginModel
import org.junit.Assert.*
import org.junit.Test

class DeviceLoginTests {
    private class Store(var value: ProfileSnapshot = ProfileSnapshot()) : ProfileStore {
        override fun load() = value
        override fun save(snapshot: ProfileSnapshot) { value = snapshot }
    }

    @Test fun signInRetryKeepsTheOneTimeToken() = runBlocking {
        withContext(Dispatchers.Main) {
            val store = Store()
            var codes = 0
            var users = 0
            val transport = ApiTransport { path, _, _, _ -> when (path) {
                "device-authorization" -> {
                    codes++
                    """{"device_code":"fixture","user_code":"123456","verification_uri":"https://example.test","expires_at":"2099-01-01T00:00:00Z","poll_interval_seconds":1}"""
                }
                "device-authorization/token" -> """{"status":"authorized","access_token":"one-time"}"""
                "users/me" -> { if (++users == 1) throw APIError(503, "Offline"); """{"id":1,"username":"Alex"}""" }
                else -> error(path)
            } }
            val session = AppSession(store) { APIClient(it, transport) }
            val login = DeviceLoginModel(session)
            assertFalse(login.run())
            assertTrue(session.hasPendingSignIn)
            assertEquals("one-time", store.value.pendingToken)
            assertTrue(login.run())
            assertEquals(1, codes)
            assertFalse(session.hasPendingSignIn)
            assertTrue(session.state is SessionState.Active)
        }
    }
}
