package net.seplis.tv.features.library

import androidx.activity.compose.BackHandler
import androidx.compose.runtime.*
import androidx.compose.ui.focus.FocusRequester
import net.seplis.tv.app.RetainedPage
import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.features.playback.PlaybackTarget
import net.seplis.tv.features.playback.PlaybackView
import net.seplis.tv.features.series.EpisodesView
import net.seplis.tv.features.series.Series

private sealed interface DetailPage {
    data object Detail : DetailPage
    data class Episodes(val series: Series, val season: Int?) : DetailPage
    data class Playback(val target: PlaybackTarget) : DetailPage
}

@Composable
fun MediaDetailPresentation(reference: MediaReference, api: APIClient, profileId: String, onClose: () -> Unit) {
    val pages = remember(reference) { mutableStateListOf<DetailPage>(DetailPage.Detail) }
    val focus = remember(reference) { mutableMapOf<Int, FocusRequester>() }
    var refresh by remember(reference) { mutableIntStateOf(0) }
    fun open(page: DetailPage) {
        focus[pages.lastIndex]?.saveFocusedChild()
        pages.add(page)
    }
    fun back() {
        if (pages.size == 1) onClose()
        else {
            focus.remove(pages.lastIndex)
            pages.removeAt(pages.lastIndex)
            refresh++
        }
    }
    BackHandler { back() }
    pages.forEachIndexed { index, page ->
        key(index, page) {
            RetainedPage(index == pages.lastIndex, remember(index, page) { focus.getOrPut(index) { FocusRequester() } }) {
                when (page) {
                    DetailPage.Detail -> MediaDetailView(reference, api,
                        onEpisodes = { series, season -> open(DetailPage.Episodes(series, season)) },
                        onPlay = { open(DetailPage.Playback(it)) }, refresh = refresh)
                    is DetailPage.Episodes -> EpisodesView(reference, page.series, page.season, api, refresh,
                        onPlay = { open(DetailPage.Playback(it)) })
                    is DetailPage.Playback -> PlaybackView(page.target, api, profileId,
                        onClose = ::back, onFinished = ::back,
                        onNext = { pages[pages.lastIndex] = DetailPage.Playback(it) })
                }
            }
        }
    }
}
