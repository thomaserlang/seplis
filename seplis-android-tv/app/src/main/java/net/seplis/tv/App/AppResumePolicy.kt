package net.seplis.tv.app

class AppResumePolicy {
    private var backgroundedAt: Long? = null
    fun background(now: Long) { if (backgroundedAt == null) backgroundedAt = now }
    fun resume(now: Long): Boolean {
        val start = backgroundedAt
        backgroundedAt = null
        return start != null && now - start >= 15 * 60 * 1000L
    }
}
