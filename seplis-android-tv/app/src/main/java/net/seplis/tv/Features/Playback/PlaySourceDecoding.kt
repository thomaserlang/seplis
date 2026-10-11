package net.seplis.tv.features.playback

import net.seplis.tv.core.networking.arrayOrEmpty
import net.seplis.tv.core.networking.flag
import net.seplis.tv.core.networking.integer
import net.seplis.tv.core.networking.number
import net.seplis.tv.core.networking.objects
import net.seplis.tv.core.networking.text
import org.json.JSONObject

fun PlayStream.Companion.from(json: JSONObject) = PlayStream(
        json.text("title")?.takeIf { it.isNotEmpty() } ?: json.text("language") ?: "Unknown", json.text("language") ?: "und",
        json.integer("group_index"), json.text("codec"), json.integer("channels"), json.flag("forced") == true)

fun PlaySource.Companion.from(json: JSONObject) = PlaySource(
        json.getInt("index"), json.number("bitrate") ?: 0.0, json.text("resolution") ?: "Unknown",
        json.text("codec") ?: "Unknown", json.optInt("width"), json.optInt("height"),
        json.number("duration") ?: 0.0, json.arrayOrEmpty("audio").objects().map(PlayStream::from),
        json.arrayOrEmpty("subtitles").objects().map(PlayStream::from),
        json.text("video_color_range"), json.text("video_color_range_type"), json.text("format"),
        json.text("media_type"), json.number("fps"),
        if (json.isNull("size")) null else json.optLong("size"))
