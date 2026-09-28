package net.seplis.tv.debug

import net.seplis.tv.app.AppSession
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.core.networking.ApiTransport
import net.seplis.tv.core.security.Profile
import net.seplis.tv.core.security.ProfileSnapshot
import net.seplis.tv.core.security.ProfileStore
import org.json.JSONArray
import org.json.JSONObject

object UITestFixtures {
    fun session(): AppSession {
        val responses = FixtureResponses()
        val store = object : ProfileStore {
            var snapshot = ProfileSnapshot(listOf(Profile(1, "Alex", "fixture-one"),
                Profile(2, "Sam", "fixture-two")), activeID = 1)
            override fun load() = snapshot
            override fun save(snapshot: ProfileSnapshot) { this.snapshot = snapshot }
        }
        return AppSession(store) { ApiClient(it, responses) }
    }
}

// The same titles and states as Apple TV's Debug/UITestFixtures.swift.
internal class FixtureResponses : ApiTransport {
    private val watches = mutableMapOf("movies/1" to 1, "series/1/episodes/1" to 1)
    private val watchlists = mutableMapOf("movies/1" to true)
    private val favorites = mutableMapOf("series/1" to true)
    private val positions = mutableMapOf<String, Int>()
    private val settings = JSONObject()

    private fun watched(path: String) = JSONObject().put("times", watches[path] ?: 0).put("position", positions[path] ?: 0)
    private fun media(movie: Boolean, id: Int = 1): JSONObject {
        val path = if (movie) "movies/$id" else "series/$id"
        return JSONObject().put("id", id)
            .put("title", if (!movie) "NCIS" else if (id == 1) "National Treasure" else "National Treasure: Book of Secrets")
            .put("tagline", if (movie) "In order to break the code..." else "The team is back.")
            .put("plot", if (movie) "A historian follows clues to a hidden treasure." else "Special agents investigate crimes connected to the Navy.")
            .put("status", 1).put("runtime", if (movie) 131 else 43).put("language", "en")
            .put("rating", if (movie) 6.9 else 7.8)
            .put("poster_image", JSONObject().put("url", "file:///android_asset/${if (movie) "movie" else "series"}.jpg"))
            .put("user_watched", watched(path))
            .put("user_watchlist", JSONObject().put("on_watchlist", watchlists[path] == true))
            .put("user_favorite", JSONObject().put("favorite", favorites[path] == true))
            .apply {
                if (movie) {
                    put("genres", JSONArray().put(JSONObject().put("name", "Adventure")))
                    put("release_date", if (id == 1) "2004-11-19" else "2007-12-21")
                    put("budget", 100_000_000).put("revenue", 348_000_000)
                    put("collection", JSONObject().put("id", 7).put("name", "National Treasure Collection"))
                } else {
                    put("premiered", "2003-09-23").put("total_episodes", 2)
                    put("seasons", JSONArray().put(JSONObject().put("season", 1).put("total", 2)))
                }
            }
    }

    private fun episode(number: Int) = JSONObject().put("number", number).put("season", 1).put("episode", number)
        .put("title", if (number == 1) "Yankee White" else "Hung Out to Dry")
        .put("air_date", if (number == 1) "2003-09-23" else "2003-09-30")
        .put("plot", if (number == 1) "A Navy commander dies aboard Air Force One." else "The team investigates a Marine's death during training.")
        .put("runtime", 43).put("user_watched", watched("series/1/episodes/$number"))
        .put("user_can_watch", JSONObject().put("on_play_server", true))

    private fun page(vararg records: Any) = JSONObject().put("records", JSONArray(records.toList())).put("cursor", JSONObject.NULL)

    override suspend fun request(path: String, method: String, query: List<Pair<String, String>>, body: JSONObject?): String =
        requestFixture(path, method, query, body)

    @Synchronized
    private fun requestFixture(path: String, method: String, query: List<Pair<String, String>>, body: JSONObject?): String {
        val parent = path.substringBeforeLast('/')
        val response: Any = when {
            path.endsWith("/watched") && path != "users/me/watched" -> {
                if (method != "GET") positions.remove(parent)
                watches[parent] = ((watches[parent] ?: 0) + when (method) { "POST" -> 1; "DELETE" -> -1; else -> 0 }).coerceAtLeast(0)
                watched(parent)
            }
            path.endsWith("/watched-position") -> {
                positions[parent] = body?.optInt("position") ?: 0
                JSONObject()
            }
            path.endsWith("/user-settings") -> {
                if (method == "PUT" && body != null) body.keys().forEach { settings.put(it, body.get(it)) }
                settings
            }
            path.endsWith("/watchlist") -> { watchlists[parent] = method == "PUT"; JSONObject() }
            path.endsWith("/favorite") -> { favorites[parent] = method == "PUT"; JSONObject() }
            path == "users/me" -> JSONObject().put("id", 1).put("username", "Alex")
            path == "genres" -> JSONArray().put(JSONObject().put("id", 1).put("name", "Adventure"))
            path == "search" -> JSONArray().put(media(true).put("type", "movie")).put(media(false).put("type", "series"))
            path == "users/me/watched" -> page(JSONObject().put("type", "movie").put("data", media(true)),
                JSONObject().put("type", "series").put("data", media(false)))
            path == "movies" -> if (query.any { it.first == "collection_id" }) page(media(true), media(true, 2)) else page(media(true))
            path == "series" -> page(media(false))
            path == "series/to-watch" || path == "series/recently-aired" -> page(JSONObject().put("series", media(false)).put("episode", episode(2)))
            path.endsWith("/episode-to-watch") -> episode(2)
            path.endsWith("/episode-last-watched") -> episode(1)
            path.endsWith("/episodes") -> page(episode(1), episode(2))
            path.endsWith("/cast") -> {
                val movie = path.startsWith("movies/")
                val names = if (movie) listOf("Alex Actor", "Morgan Reed", "Taylor Vale")
                    else listOf("Jordan Lee", "Riley Stone", "Sam Walker")
                page(*names.mapIndexed { index, name ->
                    JSONObject().put("person", JSONObject().put("id", index + if (movie) 1 else 11).put("name", name))
                        .apply {
                            if (movie) put("character", "Character ${index + 1}")
                            else put("roles", JSONArray()
                                .put(JSONObject().put("character", "Role ${index + 1}"))
                                .put(JSONObject().put("character", "Alias ${index + 1}")))
                        }
                }.toTypedArray())
            }
            path.endsWith("/play-servers") && (path.startsWith("movies/") ||
                path.matches(Regex("series/1/episodes/[12]/play-servers"))) -> JSONArray().put(
                JSONObject().put("play_id", "fixture").put("play_url", "https://play.example.test"))
            path.endsWith("/play-servers") -> JSONArray()
            path == "movies/1" -> media(true)
            path == "movies/2" -> media(true, 2)
            path == "series/1" -> media(false)
            path.matches(Regex("series/1/episodes/[12]")) -> episode(path.substringAfterLast('/').toInt())
            path == "device-authorization" -> JSONObject().put("device_code", "fixture-device")
                .put("user_code", "123456").put("verification_uri", "https://seplis.net/device")
                .put("verification_uri_complete", "https://seplis.net/device?code=123456")
                .put("expires_at", "2099-01-01T00:00:00Z").put("poll_interval_seconds", 3)
            path == "device-authorization/token" -> JSONObject().put("status", "pending")
            else -> error("Unhandled fixture request: $method $path")
        }
        return response.toString()
    }
}
