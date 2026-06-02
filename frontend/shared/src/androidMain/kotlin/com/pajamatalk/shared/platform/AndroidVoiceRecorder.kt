package com.pajamatalk.shared.platform

import android.Manifest
import android.app.Activity
import android.content.Context
import android.content.ContextWrapper
import android.content.pm.PackageManager
import android.media.MediaRecorder
import android.os.Build
import android.util.Base64
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import com.pajamatalk.shared.data.VoiceAudioChunkDto
import java.io.File

private const val RECORD_AUDIO_REQUEST_CODE = 7714

private class AndroidVoiceRecorder(private val context: Context) : PlatformVoiceRecorder {
    override val isSupported: Boolean = true

    override var isRecording by mutableStateOf(false)
        private set

    override var status by mutableStateOf(VoiceRecorderStatus.Idle)
        private set

    override var error by mutableStateOf<String?>(null)
        private set

    private var recorder: MediaRecorder? = null
    private var outputFile: File? = null
    private var startedAt = 0L

    override suspend fun start() {
        if (isRecording) return
        if (context.checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            context.findActivity()?.requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), RECORD_AUDIO_REQUEST_CODE)
            error = "record-audio-permission-needed"
            return
        }

        runCatching {
            val file = File.createTempFile("pajamatalk-voice-", ".m4a", context.cacheDir)
            val nextRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) MediaRecorder(context) else MediaRecorder()
            nextRecorder.setAudioSource(MediaRecorder.AudioSource.MIC)
            nextRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            nextRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            nextRecorder.setAudioEncodingBitRate(96_000)
            nextRecorder.setAudioSamplingRate(44_100)
            nextRecorder.setOutputFile(file.absolutePath)
            nextRecorder.prepare()
            nextRecorder.start()
            recorder = nextRecorder
            outputFile = file
            startedAt = System.currentTimeMillis()
            error = null
            status = VoiceRecorderStatus.Recording
            isRecording = true
        }.onFailure {
            error = "recording-start-failed"
            reset()
        }
    }

    override suspend fun stop(): PlatformVoiceRecording? {
        val activeRecorder = recorder ?: return null
        val file = outputFile ?: return null
        status = VoiceRecorderStatus.Processing
        isRecording = false
        return runCatching {
            activeRecorder.stop()
            activeRecorder.release()
            recorder = null
            outputFile = null
            val bytes = file.readBytes()
            file.delete()
            status = VoiceRecorderStatus.Idle
            PlatformVoiceRecording(
                chunks = listOf(
                    VoiceAudioChunkDto(
                        audioBase64 = Base64.encodeToString(bytes, Base64.NO_WRAP),
                        mimeType = "audio/mp4",
                    ),
                ),
                durationMs = (System.currentTimeMillis() - startedAt).coerceAtLeast(0),
                bytes = bytes.size.toLong(),
            )
        }.onFailure {
            error = "recording-stop-failed"
            reset()
        }.getOrNull()
    }

    override fun reset() {
        runCatching { recorder?.release() }
        recorder = null
        outputFile?.delete()
        outputFile = null
        isRecording = false
        status = VoiceRecorderStatus.Idle
    }
}

@Composable
actual fun rememberPlatformVoiceRecorder(languageCode: String): PlatformVoiceRecorder {
    val context = LocalContext.current
    return remember(context, languageCode) { AndroidVoiceRecorder(context) }
}

private tailrec fun Context.findActivity(): Activity? = when (this) {
    is Activity -> this
    is ContextWrapper -> baseContext.findActivity()
    else -> null
}
