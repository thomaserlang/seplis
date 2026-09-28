package net.seplis.tv.features.playback

import net.seplis.tv.core.networking.arrayOrEmpty
import net.seplis.tv.core.networking.objects
import net.seplis.tv.core.networking.text
import org.json.JSONObject

data class TranscodeDecision(
    val method: String, val directPlay: DirectPlayDecision, val video: StreamDecision, val audio: StreamDecision,
) {
    val playbackMethod: String get() = if (method == "transcode") "Transcoding" else "Direct Stream"
    val reasons: List<String> get() = buildList {
        if (method == "direct_play") add("Player selected HLS delivery.")
        addAll(directPlay.blockers.map { it.label })
        if (video.action == "transcode") addAll(video.blockers.map { it.label })
        if (audio.action == "transcode") addAll(audio.blockers.map { it.label })
    }.distinct()

    companion object {
        fun from(json: JSONObject) = TranscodeDecision(json.getString("method"),
            DirectPlayDecision(json.getJSONObject("direct_play").arrayOrEmpty("blockers").objects().map(PlaybackBlocker::from)),
            StreamDecision.from(json.getJSONObject("video")), StreamDecision.from(json.getJSONObject("audio")))
    }
}

data class DirectPlayDecision(val blockers: List<PlaybackBlocker>)

data class StreamDecision(val action: String, val sourceCodec: String, val targetCodec: String,
    val blockers: List<PlaybackBlocker>) {
    val label: String get() = if (action == "copy") "${sourceCodec.uppercase()} (copy)"
        else "${sourceCodec.uppercase()} -> ${targetCodec.uppercase()} (transcode)"

    companion object {
        fun from(json: JSONObject) = StreamDecision(json.getString("action"), json.getString("source_codec"),
            json.getString("target_codec"), json.arrayOrEmpty("blockers").objects().map(PlaybackBlocker::from))
    }
}

data class PlaybackBlocker(val code: String, val scope: String, val limitKind: String?) {
    val label: String get() {
        val reason = when (code) {
            "forced" -> "Transcoding requested"
            "unsupported_codec" -> "Unsupported codec"
            "unsupported_hdr" -> "Unsupported HDR format"
            "limit_exceeded" -> "${(limitKind ?: "playback").replace('_', ' ')} limit exceeded"
            "missing_keyframes" -> "Missing keyframes"
            "video_transcode_requires_audio_transcode" -> "Video transcoding requires audio transcoding"
            "unsupported_container" -> "Unsupported container"
            "client_audio_track_switch_unsupported" -> "Selected audio track requires transcoding"
            else -> code.replace('_', ' ')
        }
        return "${scope.replaceFirstChar(Char::uppercase)}: $reason"
    }

    companion object {
        fun from(json: JSONObject) = PlaybackBlocker(json.getString("code"), json.getString("scope"), json.text("limit_kind"))
    }
}
