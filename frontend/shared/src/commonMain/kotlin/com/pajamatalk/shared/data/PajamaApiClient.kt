package com.pajamatalk.shared.data

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.plugins.websocket.WebSockets
import io.ktor.client.request.bearerAuth
import io.ktor.client.request.get
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

    suspend fun words(token: String): List<WordDto> =
        client.get("$baseUrl/words") {
            bearerAuth(token)
        }.body()

    suspend fun enrichWord(token: String, term: String, sourceContext: String = ""): WordDto =
        client.post("$baseUrl/words/enrich") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(WordEnrichRequest(term, sourceContext))
        }.body()

    suspend fun reviewWord(token: String, wordId: Int, grade: ReviewGrade): ReviewDto =
        client.post("$baseUrl/words/$wordId/review") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(ReviewRequest(grade.value))
        }.body()

    suspend fun analyzeContext(token: String, text: String): ContextAnalyzeDto =
        client.post("$baseUrl/context/analyze") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(ContextAnalyzeRequest(text))
        }.body()

    suspend fun speakingRooms(token: String): List<SpeakingRoomDto> =
        client.get("$baseUrl/speaking/rooms") {
            bearerAuth(token)
        }.body()
}

enum class ReviewGrade(val value: String) {
    Remember("remember"),
    Forgot("forgot"),
}

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
    @SerialName("ai_tone") val aiTone: String,
)

@Serializable
data class WordEnrichRequest(
    val term: String,
    @SerialName("source_context") val sourceContext: String = "",
    @SerialName("target_language") val targetLanguage: String = "Ukrainian",
)

@Serializable
data class WordDto(
    val id: Int,
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
