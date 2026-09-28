package net.seplis.tv.app

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import net.seplis.tv.core.networking.ApiClient
import net.seplis.tv.core.networking.ApiException
import net.seplis.tv.core.networking.text
import net.seplis.tv.core.security.Profile
import net.seplis.tv.core.security.ProfileSnapshot
import net.seplis.tv.core.security.ProfileStore

sealed interface SessionState {
    data object Loading : SessionState
    data object SignedOut : SessionState
    data object ChooseProfile : SessionState
    data object RestoreFailed : SessionState
    data class Active(val profile: Profile, val api: ApiClient) : SessionState
}

class AppSession(private val vault: ProfileStore, private val makeClient: (String?) -> ApiClient = { ApiClient(it) }) {
    var state: SessionState by mutableStateOf(SessionState.Loading)
        private set
    var profiles: List<Profile> by mutableStateOf(emptyList())
        private set
    var error: String? by mutableStateOf(null)
    private var snapshot = ProfileSnapshot()
    val authorizationAPI: ApiClient get() = makeClient(null)
    val hasPendingSignIn get() = snapshot.pendingToken != null
    fun needsSignIn(profile: Profile) = profile.token == null

    suspend fun retryPendingSignIn() {
        val token = snapshot.pendingToken ?: return
        try { completeSignIn(token) }
        catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
        catch (failure: Exception) {
            if (state == SessionState.ChooseProfile) activateSaved()
            error = failure.message
        }
    }

    private fun active(profile: Profile): SessionState.Active {
        val client = makeClient(profile.token)
        client.onUnauthorized = {
            val stored = snapshot.profiles.firstOrNull { it.id == profile.id && it.token == profile.token }
            if (stored != null) try {
                update(snapshot.copy(profiles = snapshot.profiles.map {
                    if (it.id == profile.id) it.copy(token = null) else it
                }, activeID = snapshot.activeID.takeUnless { it == profile.id }))
                if ((state as? SessionState.Active)?.profile?.id == profile.id) activateSaved()
            } catch (failure: Exception) { error = failure.message }
        }
        return SessionState.Active(profile, client)
    }

    suspend fun restore() {
        state = SessionState.Loading
        error = null
        try {
            snapshot = vault.load()
            profiles = snapshot.profiles
            val pending = snapshot.pendingToken
            if (pending != null) {
                try { completeSignIn(pending) }
                catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
                catch (failure: Exception) { error = failure.message }
            }
            if (state !is SessionState.Active) activateSaved()
        } catch (cancelled: kotlinx.coroutines.CancellationException) { throw cancelled }
        catch (failure: Exception) {
            error = "Saved profiles could not be loaded: ${failure.message}"
            state = SessionState.RestoreFailed
        }
    }

    suspend fun signIn(token: String) {
        update(snapshot.copy(pendingToken = token))
        completeSignIn(token)
    }

    private suspend fun completeSignIn(token: String) {
        val user = try {
            makeClient(token).objectAt("users/me")
        } catch (failure: ApiException) {
            if (failure.status == 401) update(snapshot.copy(pendingToken = null))
            throw failure
        }
        val profile = Profile(user.getInt("id"), user.text("username") ?: "Account", token)
        update(snapshot.copy(
            profiles = snapshot.profiles.filterNot { it.id == profile.id } + profile,
            activeID = profile.id, pendingToken = null,
        ))
        state = active(profile)
        error = null
    }

    fun switch(profile: Profile) {
        val token = profile.token ?: return
        try {
            update(snapshot.copy(activeID = profile.id))
            state = active(profile)
            error = null
        } catch (failure: Exception) { error = failure.message }
    }

    fun startAddingAccount() { state = SessionState.SignedOut }

    fun showProfiles() { state = SessionState.ChooseProfile }

    fun returnToProfile() { activateSaved() }

    fun remove(profile: Profile) {
        try {
            val remaining = snapshot.profiles.filterNot { it.id == profile.id }
            update(snapshot.copy(profiles = remaining,
                activeID = if (snapshot.activeID == profile.id) remaining.firstOrNull { it.token != null }?.id else snapshot.activeID))
            if (state !is SessionState.Active || (state as? SessionState.Active)?.profile?.id == profile.id) activateSaved()
        } catch (failure: Exception) { error = failure.message }
    }

    private fun activateSaved() {
        val profile = snapshot.profiles.firstOrNull { it.id == snapshot.activeID && it.token != null }
        state = when {
            profile != null -> active(profile)
            snapshot.profiles.isNotEmpty() || snapshot.pendingToken != null -> SessionState.ChooseProfile
            else -> SessionState.SignedOut
        }
    }

    private fun update(value: ProfileSnapshot) {
        vault.save(value)
        snapshot = value
        profiles = value.profiles
    }
}
