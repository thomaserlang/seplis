package net.seplis.tv.app

import android.content.Context
import net.seplis.tv.core.security.ProfileVault

object SessionFactory {
    fun playServer(): net.seplis.tv.features.playback.PlayServer = net.seplis.tv.features.playback.PlayServerClient()
    fun create(context: Context) = AppSession(ProfileVault(context))
}
