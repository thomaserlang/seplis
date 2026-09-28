package net.seplis.tv

import kotlinx.coroutines.runBlocking
import net.seplis.tv.core.networking.ApiClient
import org.junit.Assert.assertTrue
import org.junit.Test

class FixtureTests {
    @Test fun fixtureBuildRejectsLiveClients() = runBlocking {
        assertTrue(BuildConfig.USE_FIXTURES)
        val error = runCatching { ApiClient("fixture-token").objectAt("users/me") }.exceptionOrNull()
        assertTrue(error is IllegalStateException)
        assertTrue(error?.message?.contains("cannot use the live API") == true)
    }
}
