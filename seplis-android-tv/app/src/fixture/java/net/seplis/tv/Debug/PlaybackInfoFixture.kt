package net.seplis.tv.debug

import net.seplis.tv.features.playback.*
import org.json.JSONObject

// playback.mp4: excerpt of Big Buck Bunny, Blender Foundation, CC BY 3.0.
// https://peach.blender.org/about/ - local video; server decisions and track choices are fixtures.
class PlaybackInfoFixture : PlayServer {
    override suspend fun sources(requests: List<PlayRequest>): List<PlayCandidate> {
        check(requests.isNotEmpty()) { "No play server is available" }
        val audio = listOf(
            PlayStream("English", "eng", 0, "aac", 2, false),
            PlayStream("Japanese", "jpn", 1, "aac", 2, false))
        val subtitles = listOf(PlayStream("English", "eng", 0, "webvtt", null, false))
        return listOf(25_000_000.0, 8_000_000.0).mapIndexed { index, bitrate ->
            PlayCandidate(requests.first(), PlaySource(index, bitrate, "720p", "h264", 320, 180,
                120.0, audio, subtitles, "SDR", null, "mp4", "video/mp4", 24.0, 12_000_000))
        }
    }

    override suspend fun open(candidate: PlayCandidate, capabilities: PlaybackCapabilities,
        audioKey: String?, subtitleKey: String?, forceTranscode: Boolean, compatibilityFallback: Boolean): PlaySession {
        val transcode = forceTranscode || candidate.source.bitrate > capabilities.maxBitrate
        val decision = JSONObject().put("method", if (transcode) "transcode" else "direct_play")
            .put("direct_play", JSONObject().put("blockers", org.json.JSONArray()))
            .put("video", JSONObject().put("action", if (transcode) "transcode" else "copy")
                .put("source_codec", "h264").put("target_codec", "h264").put("blockers", org.json.JSONArray()))
            .put("audio", JSONObject().put("action", "copy").put("source_codec", "aac")
                .put("target_codec", "aac").put("blockers", org.json.JSONArray()))
        return PlaySession("asset:///playback.mp4", "fixture:keep-alive", "fixture:close", TranscodeDecision.from(decision))
    }

    override suspend fun keepAlive(session: PlaySession) = Unit
    override suspend fun close(session: PlaySession) = Unit
}
