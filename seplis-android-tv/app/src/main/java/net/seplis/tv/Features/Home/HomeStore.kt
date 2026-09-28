package net.seplis.tv.features.home

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import net.seplis.tv.core.networking.ApiClient
import kotlinx.coroutines.CancellationException

class HomeStore(api: ApiClient) {
    private val repository = HomeRepository(api)
    private val shelves = HomeShelf.entries.associateWith { HomeShelfModel(repository, it) }
    var focusClaimed by mutableStateOf(false)
    var focusedKey: String? by mutableStateOf(null)
    var focusedShelf: HomeShelf? by mutableStateOf(null)
    var restoreFocusPending = false
    fun shelf(value: HomeShelf): HomeShelfModel = shelves.getValue(value)
}
