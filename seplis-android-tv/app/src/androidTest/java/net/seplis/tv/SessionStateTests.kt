package net.seplis.tv

import kotlinx.coroutines.*
import net.seplis.tv.app.*
import net.seplis.tv.core.networking.*
import net.seplis.tv.core.security.*
import org.junit.Assert.*
import org.junit.Test

class SessionStateTests {
    private class Store(var value: ProfileSnapshot = ProfileSnapshot()) : ProfileStore {
        override fun load() = value
        override fun save(snapshot: ProfileSnapshot) { value = snapshot }
    }

    @Test fun unauthorizedRequestsExpireOnlyTheirAccount() = runBlocking {
        withContext(Dispatchers.Main) {
            val store = Store(ProfileSnapshot(listOf(Profile(1, "Alex", "one"), Profile(2, "Sam", "two")), 1))
            val session = AppSession(store) { APIClient(it, ApiTransport { _, _, _, _ -> throw APIError(401, "Expired") }) }
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

    @Test fun pendingTokenCanBeFinishedWithoutANewDeviceCode() = runBlocking {
        withContext(Dispatchers.Main) {
            val store = Store(ProfileSnapshot(pendingToken = "saved"))
            var offline = true
            val session = AppSession(store) { APIClient(it, ApiTransport { path, _, _, _ ->
                assertEquals("users/me", path)
                if (offline) throw APIError(503, "Offline")
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
