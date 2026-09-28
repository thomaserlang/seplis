package net.seplis.tv

import kotlinx.coroutines.*
import net.seplis.tv.app.*
import net.seplis.tv.core.networking.*
import net.seplis.tv.core.security.*
import net.seplis.tv.features.authentication.DeviceLoginModel
import org.junit.Assert.*
import org.junit.Test

class AppSessionTests {
    private class Store(var value: ProfileSnapshot = ProfileSnapshot()) : ProfileStore {
        override fun load() = value
        override fun save(snapshot: ProfileSnapshot) { value = snapshot }
    }

    @Test fun unauthorizedRequestsExpireOnlyTheirAccount() = runBlocking {
        withContext(Dispatchers.Main) {
            val store = Store(ProfileSnapshot(listOf(Profile(1, "Alex", "one"), Profile(2, "Sam", "two")), 1))
            val session = AppSession(store) { ApiClient(it, ApiTransport { _, _, _, _ -> throw ApiException(401, "Expired") }) }
            session.restore()
            val old = (session.state as SessionState.Active).api
            session.switch(session.profiles[1])
            runCatching { old.objectAt("movies") }
            assertEquals(2, (session.state as SessionState.Active).profile.id)
            assertNull(session.profiles.first().token)
            runCatching { (session.state as SessionState.Active).api.objectAt("movies") }
            assertEquals(SessionState.ChooseProfile, session.state)
        }
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
                "users/me" -> { if (++users == 1) throw ApiException(503, "Offline"); """{"id":1,"username":"Alex"}""" }
                else -> error(path)
            } }
            val session = AppSession(store) { ApiClient(it, transport) }
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

    @Test fun pendingTokenCanBeFinishedWithoutANewDeviceCode() = runBlocking {
        withContext(Dispatchers.Main) {
            val store = Store(ProfileSnapshot(pendingToken = "saved"))
            var offline = true
            val session = AppSession(store) { ApiClient(it, ApiTransport { path, _, _, _ ->
                assertEquals("users/me", path)
                if (offline) throw ApiException(503, "Offline")
                """{"id":1,"username":"Alex"}"""
            }) }
            session.restore()
            assertTrue(session.hasPendingSignIn)
            offline = false
            session.retryPendingSignIn()
            assertTrue(session.state is SessionState.Active)
        }
    }
}
