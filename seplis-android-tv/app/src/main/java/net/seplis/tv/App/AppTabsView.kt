package net.seplis.tv.app

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.unit.dp
import net.seplis.tv.features.profiles.AccountMenuTrigger
import net.seplis.tv.features.profiles.ProfilesPanel
import net.seplis.tv.features.library.CatalogView
import net.seplis.tv.features.library.CatalogModel
import net.seplis.tv.features.search.SearchView
import net.seplis.tv.features.search.SearchModel
import net.seplis.tv.features.library.MediaKind
import net.seplis.tv.features.library.MediaReference
import net.seplis.tv.features.library.MediaDetailPresentation
import net.seplis.tv.features.home.HomeView
import net.seplis.tv.features.home.HomeViewState
import net.seplis.tv.components.LibraryStyle
import net.seplis.tv.components.TvButton
import androidx.compose.material.icons.filled.Search
import net.seplis.tv.features.topshelf.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.height
import kotlinx.coroutines.delay
import androidx.compose.ui.Alignment
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.res.painterResource
import androidx.compose.material.icons.Icons
import net.seplis.tv.R

internal sealed interface Screen {
    data object Home : Screen
    data object Series : Screen
    data object Movies : Screen
    data object Search : Screen
}

@Composable
internal fun AppTabsView(session: AppSession, active: SessionState.Active) {
    var base by remember(active.profile.id) { mutableStateOf<Screen>(Screen.Home) }
    val visited = remember(active.profile.id) { mutableStateListOf<Screen>(Screen.Home) }
    var isInitialHome by remember(active.profile.id) { mutableStateOf(true) }
    fun activate(screen: Screen) {
        if (base == screen) return
        isInitialHome = false
        if (screen !in visited) visited.add(screen)
        base = screen
    }
    var selectedMedia by remember(active.profile.id) { mutableStateOf<MediaReference?>(null) }
    val pageFocus = remember { FocusRequester() }
    var refresh by remember { mutableIntStateOf(0) }
    var profileMenuOpen by remember { mutableStateOf(false) }
    var contentEntry by remember { mutableStateOf<Pair<Screen, Int>?>(null) }
    var contentEntrySequence by remember { mutableIntStateOf(0) }
    var restoreMenuFocus by remember(active.profile.id) { mutableStateOf(false) }
    val activeTabFocus = remember { FocusRequester() }
    val api = active.api
    val homeStore = remember(api) { HomeViewState(api) }
    val seriesStore = remember(api) { CatalogModel(MediaKind.SERIES, api) }
    val moviesStore = remember(api) { CatalogModel(MediaKind.MOVIE, api) }
    val searchStore = remember(api) { SearchModel(api) }
    LaunchedEffect(profileMenuOpen, active.profile.id) {
        if (!profileMenuOpen && restoreMenuFocus) {
            activeTabFocus.requestFocus()
            restoreMenuFocus = false
        }
    }

    fun closeDetails() {
        selectedMedia = null
        if (base == Screen.Home) homeStore.restoreFocusPending = true
        refresh++
    }

    BackHandler(enabled = selectedMedia == null) {
        if (profileMenuOpen) profileMenuOpen = false else activeTabFocus.requestFocus()
    }

    Box(Modifier.fillMaxSize().background(LibraryStyle.background)) {
        RetainedPage(selectedMedia == null, pageFocus) {
            Column(Modifier.fillMaxSize()) {
                AppTabBar(base, active.profile.username, activeTabFocus,
                    profileMenuOpen = profileMenuOpen,
                    onSelect = { contentEntry = null; activate(it) },
                    onProfiles = {
                        restoreMenuFocus = true
                        profileMenuOpen = true
                    },
                    onEnterContent = {
                        activate(it)
                        contentEntrySequence++
                        contentEntry = it to contentEntrySequence
                    })
                Box(Modifier.fillMaxSize()) {
                    visited.forEach { tab ->
                        androidx.compose.runtime.key(tab) {
                            RetainedPage(base == tab, remember { FocusRequester() }, restoreFocusOnActivate = false) {
                                val entry = contentEntry?.takeIf { it.first == tab && base == tab }?.second ?: 0
                                val openDetail: (MediaReference) -> Unit = { ref ->
                                    contentEntry = null
                                    pageFocus.saveFocusedChild()
                                    selectedMedia = ref
                                }
                                when (tab) {
                                    Screen.Home -> HomeView(homeStore, refresh, entry,
                                        onMenuFocus = { activeTabFocus.requestFocus() }, onOpen = openDetail,
                                        isActive = base == tab && selectedMedia == null, autoFocusOnLoad = isInitialHome)
                                    Screen.Series -> CatalogView(MediaKind.SERIES, seriesStore, refresh, entry,
                                        onMenuFocus = { activeTabFocus.requestFocus() }, onOpen = openDetail,
                                        isActive = base == tab && selectedMedia == null)
                                    Screen.Movies -> CatalogView(MediaKind.MOVIE, moviesStore, refresh, entry,
                                        onMenuFocus = { activeTabFocus.requestFocus() }, onOpen = openDetail,
                                        isActive = base == tab && selectedMedia == null)
                                    Screen.Search -> SearchView(searchStore, refresh, entry,
                                        onMenuFocus = { activeTabFocus.requestFocus() }, onOpen = openDetail,
                                        isActive = base == tab && selectedMedia == null)
                                }
                            }
                        }
                    }
                }
            }
        }
        selectedMedia?.let { reference ->
            MediaDetailPresentation(reference, api, active.profile.id.toString(), onClose = ::closeDetails)
        }
        if (profileMenuOpen) {
            ProfilesPanel(session, onClose = { profileMenuOpen = false })
        }
    }
}

@Composable
private fun AppTabBar(current: Screen, username: String, activeTabFocus: FocusRequester,
    profileMenuOpen: Boolean = false,
    onSelect: (Screen) -> Unit, onProfiles: () -> Unit,
    onEnterContent: (Screen) -> Unit) {
    var hovered by remember { mutableStateOf<Screen?>(null) }
    var profileFocused by remember { mutableStateOf(false) }
    LaunchedEffect(hovered) {
        val target = hovered ?: return@LaunchedEffect
        if (target != current) {
            delay(300)
            onSelect(target)
        }
    }
    Box(Modifier.fillMaxWidth().height(LibraryStyle.menuHeight).padding(horizontal = LibraryStyle.horizontalInset)) {
        AccountMenuTrigger(username, { profileFocused = it }, onProfiles,
            Modifier.align(Alignment.CenterStart).alpha(if (profileMenuOpen) 0f else 1f))
        Row(Modifier.align(Alignment.Center), verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf(Screen.Search to "Search", Screen.Home to "Home", Screen.Series to "Series", Screen.Movies to "Movies")
                .forEach { (screen, title) ->
                    TvButton(title, { hovered = null; onSelect(screen) },
                        modifier = if (current == screen) Modifier.focusRequester(activeTabFocus) else Modifier,
                        selected = current == screen && hovered == null && !profileFocused && !profileMenuOpen,
                        color = LibraryStyle.surfaceRaised, flat = true,
                        icon = if (screen == Screen.Search) Icons.Default.Search else null,
                        iconOnly = screen == Screen.Search,
                        onDown = { hovered = null; onEnterContent(screen) },
                        onFocusChange = { focused ->
                            if (focused) hovered = screen
                            else if (hovered == screen) hovered = null
                        })
                }
        }
        Image(painterResource(R.drawable.seplis_logo), "SEPLIS",
            Modifier.align(Alignment.CenterEnd).width(20.dp).height(20.dp).clip(RoundedCornerShape(10.dp)))
    }
}
