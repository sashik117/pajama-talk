package com.pajamatalk.shared.platform

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember

private class DesktopSpeechPlayer : PlatformSpeechPlayer {
    override val isSupported: Boolean = false

    override fun speak(text: String, languageCode: String, rate: Float) = Unit

    override fun stop() = Unit
}

@Composable
actual fun rememberPlatformSpeechPlayer(languageCode: String): PlatformSpeechPlayer = remember(languageCode) {
    DesktopSpeechPlayer()
}
