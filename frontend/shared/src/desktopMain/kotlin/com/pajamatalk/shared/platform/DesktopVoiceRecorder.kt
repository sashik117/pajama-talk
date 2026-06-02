package com.pajamatalk.shared.platform

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember

private class DesktopVoiceRecorder : PlatformVoiceRecorder {
    override val isSupported: Boolean = false
    override val isRecording: Boolean = false
    override val status: VoiceRecorderStatus = VoiceRecorderStatus.Idle
    override val error: String? = null

    override suspend fun start() = Unit

    override suspend fun stop(): PlatformVoiceRecording? = null

    override fun reset() = Unit
}

@Composable
actual fun rememberPlatformVoiceRecorder(languageCode: String): PlatformVoiceRecorder = remember(languageCode) {
    DesktopVoiceRecorder()
}
