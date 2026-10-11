package net.seplis.tv

import net.seplis.tv.features.playback.resolvePlayUrl
import org.junit.Assert.assertEquals
import org.junit.Test

class PlayServerTests {
    @Test fun playServerPathsStayUnderMountPoint() {
        assertEquals("https://play.example.com/mount/session/stream.m3u8",
            resolvePlayUrl("https://play.example.com/mount", "/session/stream.m3u8"))
        assertEquals("https://other.example.com/media.m3u8",
            resolvePlayUrl("https://play.example.com/mount", "https://other.example.com/media.m3u8"))
    }
}
