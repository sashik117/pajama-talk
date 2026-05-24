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
    var isAuthenticating by mutableStateOf(false)
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
    var stats by mutableStateOf<ProfileStatsDto?>(null)
        private set
    var words by mutableStateOf<List<WordDto>>(emptyList())
        private set
    var dueWords by mutableStateOf<List<WordDto>>(emptyList())
        private set
    var isDueWordsLoading by mutableStateOf(false)
        private set
    var speakingRooms by mutableStateOf<List<SpeakingRoomDto>>(emptyList())
        private set
    var speakingHints by mutableStateOf<SpeakingHintsDto?>(null)
        private set
    var isLoadingHints by mutableStateOf(false)
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
        val client = findWorkingClient()
        if (client == null) {
            isBooting = false
            errorMessage = "Backend is offline. Start FastAPI and tap Refresh."
            return
        }

        activeClient = client
        activeBaseUrl = client.baseUrl
        isBooting = false
    }

    suspend fun login(email: String, password: String) {
        authenticate {
            it.login(email.trim(), password)
        }
    }

    suspend fun register(email: String, password: String, displayName: String) {
        authenticate {
            it.register(email.trim(), password, displayName.trim().ifBlank { "Dreamer" })
        }
    }

    suspend fun continueAsDemo() {
        authenticate {
            runCatching {
                it.register(DEV_EMAIL, DEV_PASSWORD, "Dreamer")
            }.recoverCatching { error ->
                if (error is ClientRequestException && error.response.status.value == 409) {
                    it.login(DEV_EMAIL, DEV_PASSWORD)
                } else {
                    throw error
                }
            }.getOrThrow()
        }
    }

    fun logout() {
        token = null
        user = null
        stats = null
        words = emptyList()
        dueWords = emptyList()
        speakingRooms = emptyList()
        speakingHints = null
        contextResult = null
        errorMessage = null
    }

    private suspend fun authenticate(block: suspend (PajamaApiClient) -> TokenResponse) {
        isAuthenticating = true
        errorMessage = null
        val client = activeClient ?: findWorkingClient()
        if (client == null) {
            errorMessage = "Backend is offline. Start FastAPI and tap Refresh."
            isAuthenticating = false
            return
        }
        activeClient = client
        activeBaseUrl = client.baseUrl
        runCatching {
            val session = block(client)
            openSession(client, session.accessToken)
        }.onFailure { errorMessage = it.friendlyMessage() }
        isAuthenticating = false
    }

    private suspend fun openSession(client: PajamaApiClient, accessToken: String) {
        activeClient = client
        token = accessToken
        activeBaseUrl = client.baseUrl
        val profile = client.me(accessToken)
        user = profile
        selectedLanguage = languageByCode(profile.activeLanguageCode)
        speakingRooms = client.speakingRooms(accessToken, selectedLanguage.code)
        loadWords()
        loadDueWords()
        loadStats()
    }

    suspend fun refreshAll() {
        if (activeClient == null || token == null) {
            boot()
            return
        }
        errorMessage = null
        loadWords()
        loadDueWords()
        runCatching {
            user = requireClient().me(requireToken())
            speakingRooms = requireClient().speakingRooms(requireToken(), selectedLanguage.code)
            loadStats()
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

    suspend fun loadDueWords() {
        isDueWordsLoading = true
        errorMessage = null
        runCatching {
            dueWords = requireClient().dueWords(requireToken(), selectedLanguage.code)
        }.onFailure {
            errorMessage = it.friendlyMessage()
        }
        isDueWordsLoading = false
    }

    suspend fun loadStats() {
        runCatching {
            stats = requireClient().stats(requireToken())
        }.onFailure {
            errorMessage = it.friendlyMessage()
        }
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
            dueWords = listOf(created) + dueWords.filterNot { it.id == created.id }
            loadStats()
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
            dueWords = dueWords.filterNot { it.id == word.id }
            loadStats()
        }.onFailure {
            errorMessage = it.friendlyMessage()
        }
        isReviewing = false
    }

    fun clearContextResult() {
        contextResult = null
    }

    suspend fun loadSpeakingHints(roomId: String, lastMessage: String) {
        isLoadingHints = true
        errorMessage = null
        runCatching {
            speakingHints = requireClient().speakingHints(
                token = requireToken(),
                roomId = roomId,
                lastMessage = lastMessage,
                languageCode = selectedLanguage.code,
            )
        }.onFailure {
            errorMessage = it.friendlyMessage()
        }
        isLoadingHints = false
    }

    fun clearSpeakingHints() {
        speakingHints = null
    }

    suspend fun selectLanguage(language: LearningLanguage) {
        if (language.code == selectedLanguage.code) return
        selectedLanguage = language
        contextResult = null
        speakingHints = null
        words = emptyList()
        dueWords = emptyList()
        if (activeClient != null && token != null) {
            updateProfile(ProfileUpdateRequest(activeLanguageCode = language.code))
            speakingRooms = requireClient().speakingRooms(requireToken(), selectedLanguage.code)
            loadWords()
            loadDueWords()
            loadStats()
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
            loadStats()
        }.onFailure {
            errorMessage = it.friendlyMessage()
        }
    }

    private suspend fun findWorkingClient(): PajamaApiClient? {
        for (client in clients) {
            val isHealthy = runCatching { client.health() }.getOrNull()?.status == "ok"
            if (isHealthy) {
                return client
            }
        }
        return null
    }

    private fun requireClient(): PajamaApiClient =
        activeClient ?: error("Pajama API is not connected yet.")

    private fun requireToken(): String =
        token ?: error("Pajama API token is not ready yet.")

    private fun Throwable.friendlyMessage(): String =
        if (this is ClientRequestException) {
            when (response.status.value) {
                401 -> "Wrong email or password."
                409 -> "That email already has a PajamaTalk space."
                422 -> "Check the email and password fields."
                else -> message
            }
        } else {
            message
        }?.takeIf { it.isNotBlank() } ?: "Something went soft-sideways."

    private companion object {
        const val DEV_EMAIL = "dreamer@pajamatalk.dev"
        const val DEV_PASSWORD = "pajama-dev-secret"
    }
}
