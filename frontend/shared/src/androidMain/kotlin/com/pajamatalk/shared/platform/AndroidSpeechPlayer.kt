package com.pajamatalk.shared.platform

import android.content.Context
import android.speech.tts.TextToSpeech
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import java.util.Locale

private class AndroidSpeechPlayer(context: Context, languageCode: String) : PlatformSpeechPlayer, TextToSpeech.OnInitListener {
    override var isSupported by mutableStateOf(false)
        private set

    private val appContext = context.applicationContext
    private var engine: TextToSpeech? = TextToSpeech(appContext, this)
    private var currentLocale = localeForLanguage(languageCode)

    override fun onInit(status: Int) {
        val tts = engine ?: return
        isSupported = status == TextToSpeech.SUCCESS && applyLanguage(tts, currentLocale)
    }

    override fun speak(text: String, languageCode: String, rate: Float) {
        val cleanText = text.trim()
        if (cleanText.isBlank()) return

        val tts = engine ?: return
        val nextLocale = localeForLanguage(languageCode)
        if (nextLocale != currentLocale || !isSupported) {
            currentLocale = nextLocale
            isSupported = applyLanguage(tts, nextLocale)
        }
        if (!isSupported) return

        tts.setSpeechRate(rate)
        tts.speak(cleanText, TextToSpeech.QUEUE_FLUSH, null, "pajamatalk-${System.currentTimeMillis()}")
    }

    override fun stop() {
        engine?.stop()
    }

    fun shutdown() {
        engine?.stop()
        engine?.shutdown()
        engine = null
    }

    private fun applyLanguage(tts: TextToSpeech, locale: Locale): Boolean {
        val result = tts.setLanguage(locale)
        return result != TextToSpeech.LANG_MISSING_DATA && result != TextToSpeech.LANG_NOT_SUPPORTED
    }
}

@Composable
actual fun rememberPlatformSpeechPlayer(languageCode: String): PlatformSpeechPlayer {
    val context = LocalContext.current
    val player = remember(context, languageCode) { AndroidSpeechPlayer(context, languageCode) }

    DisposableEffect(player) {
        onDispose { player.shutdown() }
    }

    return player
}

private fun localeForLanguage(code: String): Locale = when (code) {
    "uk" -> Locale("uk", "UA")
    "ru" -> Locale("ru", "RU")
    "pl" -> Locale("pl", "PL")
    "sk" -> Locale("sk", "SK")
    "cs" -> Locale("cs", "CZ")
    "fr" -> Locale.FRANCE
    "es" -> Locale("es", "ES")
    "it" -> Locale.ITALY
    "de" -> Locale.GERMANY
    "pt" -> Locale("pt", "PT")
    "tr" -> Locale("tr", "TR")
    "ja" -> Locale.JAPAN
    "ko" -> Locale.KOREA
    "zh" -> Locale.SIMPLIFIED_CHINESE
    else -> Locale.UK
}
