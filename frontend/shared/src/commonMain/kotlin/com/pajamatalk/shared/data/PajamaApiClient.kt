package com.pajamatalk.shared.data

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.plugins.websocket.WebSockets
import io.ktor.client.request.bearerAuth
import io.ktor.client.request.get
import io.ktor.client.request.parameter
import io.ktor.client.request.patch
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

class PajamaApiClient(
    val baseUrl: String = "http://127.0.0.1:8000",
    private val client: HttpClient = HttpClient {
        install(ContentNegotiation) {
            json(Json { ignoreUnknownKeys = true })
        }
        install(WebSockets)
    },
) {
    suspend fun health(): HealthResponse =
        client.get("$baseUrl/health").body()

    suspend fun register(email: String, password: String, displayName: String): TokenResponse =
        client.post("$baseUrl/auth/register") {
            contentType(ContentType.Application.Json)
            setBody(RegisterRequest(email, password, displayName))
        }.body()

    suspend fun login(email: String, password: String): TokenResponse =
        client.post("$baseUrl/auth/login") {
            contentType(ContentType.Application.Json)
            setBody(LoginRequest(email, password))
        }.body()

    suspend fun me(token: String): UserDto =
        client.get("$baseUrl/auth/me") {
            bearerAuth(token)
        }.body()

    suspend fun updateProfile(token: String, payload: ProfileUpdateRequest): UserDto =
        client.patch("$baseUrl/auth/me") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(payload)
        }.body()

    suspend fun stats(token: String): ProfileStatsDto =
        client.get("$baseUrl/stats/me") {
            bearerAuth(token)
        }.body()

    suspend fun words(token: String, languageCode: String? = null): List<WordDto> =
        client.get("$baseUrl/words") {
            bearerAuth(token)
            if (languageCode != null) {
                parameter("language_code", languageCode)
            }
        }.body()

    suspend fun dueWords(token: String, languageCode: String? = null): List<WordDto> =
        client.get("$baseUrl/words/review-due") {
            bearerAuth(token)
            if (languageCode != null) {
                parameter("language_code", languageCode)
            }
        }.body()

    suspend fun enrichWord(
        token: String,
        term: String,
        sourceContext: String = "",
        languageCode: String = "en",
    ): WordDto =
        client.post("$baseUrl/words/enrich") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(WordEnrichRequest(term, languageCode, sourceContext))
        }.body()

    suspend fun reviewWord(token: String, wordId: Int, grade: ReviewGrade): ReviewDto =
        client.post("$baseUrl/words/$wordId/review") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(ReviewRequest(grade.value))
        }.body()

    suspend fun analyzeContext(token: String, text: String, languageCode: String = "en"): ContextAnalyzeDto =
        client.post("$baseUrl/context/analyze") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(ContextAnalyzeRequest(text, languageCode))
        }.body()

    suspend fun speakingRooms(token: String, languageCode: String? = null): List<SpeakingRoomDto> =
        client.get("$baseUrl/speaking/rooms") {
            bearerAuth(token)
            if (languageCode != null) {
                parameter("language_code", languageCode)
            }
        }.body()

    suspend fun speakingHints(
        token: String,
        roomId: String,
        lastMessage: String,
        languageCode: String,
    ): SpeakingHintsDto =
        client.post("$baseUrl/speaking/hints") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(SpeakingHintsRequest(roomId, lastMessage, languageCode))
        }.body()
}

enum class ReviewGrade(val value: String) {
    Remember("remember"),
    Forgot("forgot"),
}

@Serializable
data class HealthResponse(
    val status: String,
)

@Serializable
data class RegisterRequest(
    val email: String,
    val password: String,
    @SerialName("display_name") val displayName: String,
)

@Serializable
data class LoginRequest(
    val email: String,
    val password: String,
)

@Serializable
data class TokenResponse(
    @SerialName("access_token") val accessToken: String,
    @SerialName("token_type") val tokenType: String,
)

@Serializable
data class UserDto(
    val id: Int,
    val email: String,
    @SerialName("display_name") val displayName: String,
    @SerialName("learning_vibe") val learningVibe: String,
    @SerialName("active_language_code") val activeLanguageCode: String,
    @SerialName("native_language_code") val nativeLanguageCode: String,
    @SerialName("daily_vibe_minutes") val dailyVibeMinutes: Int,
    @SerialName("ai_tone") val aiTone: String,
)

@Serializable
data class ProfileUpdateRequest(
    @SerialName("display_name") val displayName: String? = null,
    @SerialName("learning_vibe") val learningVibe: String? = null,
    @SerialName("active_language_code") val activeLanguageCode: String? = null,
    @SerialName("native_language_code") val nativeLanguageCode: String? = null,
    @SerialName("daily_vibe_minutes") val dailyVibeMinutes: Int? = null,
    @SerialName("ai_tone") val aiTone: String? = null,
)

@Serializable
data class ProfileStatsDto(
    @SerialName("active_language_code") val activeLanguageCode: String,
    @SerialName("total_words") val totalWords: Int,
    @SerialName("language_words") val languageWords: Int,
    @SerialName("learned_words") val learnedWords: Int,
    @SerialName("due_reviews") val dueReviews: Int,
    @SerialName("daily_vibe_minutes") val dailyVibeMinutes: Int,
    @SerialName("learning_vibe") val learningVibe: String,
    @SerialName("ai_tone") val aiTone: String,
)

@Serializable
data class WordEnrichRequest(
    val term: String,
    @SerialName("language_code") val languageCode: String = "en",
    @SerialName("source_context") val sourceContext: String = "",
    @SerialName("target_language") val targetLanguage: String = "Ukrainian",
)

@Serializable
data class WordDto(
    val id: Int,
    @SerialName("language_code") val languageCode: String = "en",
    val term: String,
    val translation: String,
    val transcription: String,
    val meme: String,
    @SerialName("example_one") val exampleOne: String,
    @SerialName("example_two") val exampleTwo: String,
    @SerialName("source_context") val sourceContext: String,
    @SerialName("color_level") val colorLevel: Int,
    @SerialName("due_at") val dueAt: String? = null,
)

@Serializable
data class ReviewRequest(
    val grade: String,
)

@Serializable
data class ReviewDto(
    @SerialName("word_id") val wordId: Int,
    val grade: String,
    val repetitions: Int,
    val lapses: Int,
    @SerialName("interval_minutes") val intervalMinutes: Int,
    @SerialName("due_at") val dueAt: String,
    @SerialName("color_level") val colorLevel: Int,
)

@Serializable
data class ContextAnalyzeRequest(
    val text: String,
    @SerialName("language_code") val languageCode: String = "en",
    @SerialName("target_language") val targetLanguage: String = "Ukrainian",
)

@Serializable
data class ContextAnalyzeDto(
    val summary: String,
    @SerialName("hidden_meaning") val hiddenMeaning: String,
    val highlights: List<ContextHighlightDto>,
    @SerialName("suggested_words") val suggestedWords: List<String>,
)

@Serializable
data class ContextHighlightDto(
    val phrase: String,
    val explanation: String,
    @SerialName("addable_words") val addableWords: List<String>,
)

@Serializable
data class SpeakingRoomDto(
    val id: String,
    val title: String,
    val character: String,
    val vibe: String,
    val prompt: String,
    @SerialName("accent_color") val accentColor: String,
)

@Serializable
data class SpeakingHintsRequest(
    @SerialName("room_id") val roomId: String,
    @SerialName("last_message") val lastMessage: String,
    @SerialName("language_code") val languageCode: String,
)

@Serializable
data class SpeakingHintsDto(
    val simple: String,
    val conversational: String,
    val spicy: String,
)
