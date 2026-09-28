package net.seplis.tv.app

import net.seplis.tv.core.networking.APIClient
import net.seplis.tv.core.security.Profile

sealed interface SessionState {
    data object Loading : SessionState
    data object SignedOut : SessionState
    data object ChooseProfile : SessionState
    data object RestoreFailed : SessionState
    data class Active(val profile: Profile, val api: APIClient) : SessionState
}
