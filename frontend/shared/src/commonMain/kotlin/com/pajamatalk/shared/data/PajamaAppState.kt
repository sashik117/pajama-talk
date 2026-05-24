package com.pajamatalk.shared.data

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import io.ktor.client.plugins.ClientRequestException

class PajamaAppState(
    private val clients: List<PajamaApiClient> = listOf(
        PajamaApiClient("http://127.0.0.1:8000"),
        PajamaApiClient("http://127.0.0.1:8001"),
    ),
) {
    var isBooting by mutableStateOf(true)
        private set
    var isWordsLoading by mutableStateOf(false)
        private set
    var isAddingWord by mutableStateOf(false)
        private set
    var isAnalyzingContext by mutableStateOf(false)
        private set
    var isReviewing by mutableStateOf(false)
        private set
    var errorMessage by mutableStateOf<String?>(null)
        private set
    var activeBaseUrl by mutableStateOf<String?>(null)
        private set
    var user by mutableStateOf<UserDto?>(null)
        private set
    var words by mutableStateOf<List<WordDto>>(emptyList())
        private set
    var speakingRooms by mutableStateOf<List<SpeakingRoomDto>>(emptyList())
        private set
    var contextResult by mutableStateOf<ContextAnalyzeDto?>(null)
        private set
    var selectedLanguage by mutableStateOf(SupportedLearningLanguages.first())
        private set

    private var activeClient: PajamaApiClient? = null
    private var token: String? = null

    suspend fun boot() {
        isBooting = true
        errorMessage = null
        val login = findWorkingLogin()
        if (login == null) {
            isBooting = false
            errorMessage = "Backend is offline. Start FastAPI and tap Refresh."
            return
        }

        activeClient = login.client
        token = login.token
        activeBaseUrl = login.client.baseUrl

        runCatching {
            val profile = login.client.me(login.token)
            user = profile
            selectedLanguage = languageByCode(profile.activeLanguageCode)
            speakingRooms = login.client.speakingRooms(login.token, selectedLanguage.code)
            loadWords()
        }.onFailure { errorMessage = it.friendlyMessage() }

        isBooting = false
    }

    suspend fun refreshAll() {
        if (activeClient == null || token == null) {
            boot()
            return
        }
        errorMessage = null
        loadWords()
        runCatching {
            user = requireClient().me(requireToken())
            speakingRooms = requireClient().speakingRooms(requireToken(), selectedLanguage.code)
        }.onFailure { errorMessage = it.friendlyMessage() }
    }

    suspend fun loadWords() {
        isWordsLoading = true
        errorMessage = null
        runCatching {
            words = requireClient().words(requireToken(), selectedLanguage.code)
        }.onFailure {
            errorMessage = it.friendlyMessage()
        }
        isWordsLoading = false
    }

    suspend fun addWord(term: String, sourceContext: String = "") {
        val cleanTerm = term.trim()
        if (cleanTerm.isBlank()) return

        isAddingWord = true
        errorMessage = null
        runCatching {
            val created = requireClient().enrichWord(
                token = requireToken(),
                term = cleanTerm,
                sourceContext = sourceContext,
                languageCode = selectedLanguage.code,
            )
            words = listOf(created) + words.filterNot { it.id == created.id }
        }.onFailure {
            errorMessage = it.friendlyMessage()
        }
        isAddingWord = false
    }

    suspend fun analyzeContext(text: String) {
        val cleanText = text.trim()
        if (cleanText.length < 3) return

        isAnalyzingContext = true
        errorMessage = null
        runCatching {
            contextResult = requireClient().analyzeContext(requireToken(), cleanText, selectedLanguage.code)
        }.onFailure {
            errorMessage = it.friendlyMessage()
        }
        isAnalyzingContext = false
    }

    suspend fun addContextSuggestions() {
        val result = contextResult ?: return
        result.suggestedWords.take(5).forEach { addWord(it, result.summary) }
    }

    suspend fun reviewWord(word: WordDto, grade: ReviewGrade) {
        if (isReviewing) return

        isReviewing = true
        errorMessage = null
        runCatching {
            val review = requireClient().reviewWord(requireToken(), word.id, grade)
            words = words.map {
                if (it.id == word.id) it.copy(colorLevel = review.colorLevel, dueAt = review.dueAt) else it
            }
        }.onFailure {
            errorMessage = it.friendlyMessage()
        }
        isReviewing = false
    }

    fun clearContextResult() {
        contextResult = null
    }

    suspend fun selectLanguage(language: LearningLanguage) {
        if (language.code == selectedLanguage.code) return
        selectedLanguage = language
        contextResult = null
        words = emptyList()
        if (activeClient != null && token != null) {
            updateProfile(ProfileUpdateRequest(activeLanguageCode = language.code))
            speakingRooms = requireClient().speakingRooms(requireToken(), selectedLanguage.code)
            loadWords()
        }
    }

    suspend fun setLearningVibe(vibe: String) {
        val minutes = when (vibe) {
            "Hardcore" -> 30
            "Normal" -> 15
            else -> 5
        }
        updateProfile(ProfileUpdateRequest(learningVibe = vibe, dailyVibeMinutes = minutes))
    }

    suspend fun setAiTone(tone: String) {
        updateProfile(ProfileUpdateRequest(aiTone = tone))
    }

    private suspend fun updateProfile(payload: ProfileUpdateRequest) {
        errorMessage = null
        runCatching {
            user = requireClient().updateProfile(requireToken(), payload)
        }.onFailure {
            errorMessage = it.friendlyMessage()
        }
    }

    private suspend fun findWorkingLogin(): LoginSession? {
        for (client in clients) {
            val registered = runCatching {
                client.register(DEV_EMAIL, DEV_PASSWORD, "Dreamer")
            }.recoverCatching { error ->
                if (error is ClientRequestException && error.response.status.value == 409) {
                    client.login(DEV_EMAIL, DEV_PASSWORD)
                } else {
                    throw error
                }
            }.getOrNull()

            if (registered != null) {
                return LoginSession(client, registered.accessToken)
            }
        }
        return null
    }

    private fun requireClient(): PajamaApiClient =
        activeClient ?: error("Pajama API is not connected yet.")

    private fun requireToken(): String =
        token ?: error("Pajama API token is not ready yet.")

    private fun Throwable.friendlyMessage(): String =
        message?.takeIf { it.isNotBlank() } ?: "Something went soft-sideways."

    private data class LoginSession(
        val client: PajamaApiClient,
        val token: String,
    )

    private companion object {
        const val DEV_EMAIL = "dreamer@pajamatalk.dev"
        const val DEV_PASSWORD = "pajama-dev-secret"
    }
}
