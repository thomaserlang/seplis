package net.seplis.tv.features.library

import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.features.library.MediaReference

class MediaDetailRepository(private val api: ApiClient) {
    suspend fun update(ref: MediaReference, path: String, method: String) {
        api.perform("${ref.path}/$path", method)
        if (path.endsWith("watched")) net.seplis.tv.features.topshelf.WatchHistory.notifyChanged()
    }
}
