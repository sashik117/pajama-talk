package com.pajamatalk.shared.platform

import androidx.compose.runtime.Composable

interface PlatformSpeechPlayer {
    val isSupported: Boolean

    fun speak(text: String, languageCode: String, rate: Float = 0.92f)
    fun stop()
}

@Composable
expect fun rememberPlatformSpeechPlayer(languageCode: String): PlatformSpeechPlayer
