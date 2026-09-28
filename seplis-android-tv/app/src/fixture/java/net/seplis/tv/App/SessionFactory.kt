package net.seplis.tv.app

import android.content.Context
import net.seplis.tv.debug.UITestFixtures

object SessionFactory {
    fun playServer(): net.seplis.tv.features.playback.PlayServer = net.seplis.tv.features.playback.PlayServerClient()
    fun create(context: Context) = UITestFixtures.session()
}
