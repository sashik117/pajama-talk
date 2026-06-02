package com.pajamatalk.shared.platform

import androidx.compose.runtime.Composable
import com.pajamatalk.shared.data.VoiceAudioChunkDto

data class PlatformVoiceRecording(
    val chunks: List<VoiceAudioChunkDto>,
    val durationMs: Long,
    val bytes: Long,
)

interface PlatformVoiceRecorder {
    val isSupported: Boolean
    val isRecording: Boolean
    val status: VoiceRecorderStatus
    val error: String?

    suspend fun start()
    suspend fun stop(): PlatformVoiceRecording?
    fun reset()
}

enum class VoiceRecorderStatus {
    Idle,
    Recording,
    Processing,
}

@Composable
expect fun rememberPlatformVoiceRecorder(languageCode: String): PlatformVoiceRecorder
