package net.seplis.tv

import net.seplis.tv.app.AppResumePolicy
import org.junit.Assert.*
import org.junit.Test

class AppResumePolicyTests {
    @Test fun resetsOnlyAfterFifteenMinutesAndOnlyOnce() {
        val policy = AppResumePolicy()
        assertFalse(policy.resume(0))
        policy.background(100)
        assertFalse(policy.resume(899_999))
        policy.background(1_000_000)
        policy.background(1_100_000)
        assertTrue(policy.resume(1_900_000))
        assertFalse(policy.resume(3_000_000))
    }
}
