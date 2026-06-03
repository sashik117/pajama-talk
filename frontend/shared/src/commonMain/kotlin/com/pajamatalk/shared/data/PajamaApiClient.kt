package com.pajamatalk.shared.data

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.plugins.websocket.WebSockets
import io.ktor.client.plugins.websocket.webSocket
import io.ktor.client.request.bearerAuth
import io.ktor.client.request.get
import io.ktor.client.request.parameter
import io.ktor.client.request.patch
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.serialization.kotlinx.json.json
import io.ktor.websocket.Frame
import io.ktor.websocket.readText
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
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
    private val json = Json { ignoreUnknownKeys = true }

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

    suspend fun grammarDrops(token: String, languageCode: String? = null, targetLanguageCode: String? = null): List<GrammarDropDto> =
        client.get("$baseUrl/grammar/drops") {
            bearerAuth(token)
            if (languageCode != null) {
                parameter("language_code", languageCode)
            }
            if (targetLanguageCode != null) {
                parameter("target_language_code", targetLanguageCode)
            }
        }.body()

    suspend fun grammarTopics(token: String, languageCode: String? = null, targetLanguageCode: String? = null): List<GrammarTopicDto> =
        client.get("$baseUrl/grammar/topics") {
            bearerAuth(token)
            if (languageCode != null) {
                parameter("language_code", languageCode)
            }
            if (targetLanguageCode != null) {
                parameter("target_language_code", targetLanguageCode)
            }
        }.body()

    suspend fun checkGrammar(token: String, topicId: String, exerciseId: String, answer: String, targetLanguageCode: String? = null): GrammarCheckDto =
        client.post("$baseUrl/grammar/check") {
            bearerAuth(token)
            if (targetLanguageCode != null) {
                parameter("target_language_code", targetLanguageCode)
            }
            contentType(ContentType.Application.Json)
            setBody(GrammarCheckRequest(topicId, exerciseId, answer))
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
        targetLanguage: String = "Ukrainian",
    ): WordDto =
        client.post("$baseUrl/words/enrich") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(WordEnrichRequest(term, languageCode, sourceContext, targetLanguage))
        }.body()

    suspend fun reviewWord(token: String, wordId: Int, grade: ReviewGrade): ReviewDto =
        client.post("$baseUrl/words/$wordId/review") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(ReviewRequest(grade.value))
        }.body()

    suspend fun analyzeContext(
        token: String,
        text: String,
        languageCode: String = "en",
        targetLanguage: String = "Ukrainian",
    ): ContextAnalyzeDto =
        client.post("$baseUrl/context/analyze") {
            bearerAuth(token)
            contentType(ContentType.Application.Json)
            setBody(ContextAnalyzeRequest(text, languageCode, targetLanguage))
        }.body()

    suspend fun speakingRooms(token: String, languageCode: String? = null, targetLanguageCode: String? = null): List<SpeakingRoomDto> =
        client.get("$baseUrl/speaking/rooms") {
            bearerAuth(token)
            if (languageCode != null) {
                parameter("language_code", languageCode)
            }
            if (targetLanguageCode != null) {
                parameter("target_language_code", targetLanguageCode)
            }
        }.body()

    suspend fun speakingHistory(token: String, roomId: String, limit: Int = 40): List<SpeakingHistoryMessageDto> =
        client.get("$baseUrl/speaking/history") {
            bearerAuth(token)
            parameter("room_id", roomId)
            parameter("limit", limit)
        }.body()

    suspend fun learningPath(token: String, languageCode: String? = null, targetLanguageCode: String? = null): LearningPathDto =
        client.get("$baseUrl/learning/path") {
            bearerAuth(token)
            if (languageCode != null) {
                parameter("language_code", languageCode)
            }
            if (targetLanguageCode != null) {
                parameter("target_language_code", targetLanguageCode)
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

    suspend fun streamSpeakingReply(
        token: String,
        roomId: String,
        message: String,
        onToken: (String) -> Unit,
    ): String {
        val reply = StringBuilder()
        client.webSocket("$webSocketBaseUrl/speaking/ws?token=$token&room_id=$roomId") {
            send(Frame.Text(message))
            for (frame in incoming) {
                if (frame !is Frame.Text) continue
                val event = json.decodeFromString<SpeakingStreamEvent>(frame.readText())
                when (event.type) {
                    "token" -> {
                        val value = event.value.orEmpty()
                        reply.append(value)
                        onToken(value)
                    }
                    "done" -> break
                }
            }
        }
        return reply.toString().trim()
    }

    suspend fun streamVoiceTextReply(
        token: String,
        roomId: String,
        message: String,
        speed: Float = 1f,
        onTranscript: (String) -> Unit = {},
        onToken: (String) -> Unit,
    ): String {
        val reply = StringBuilder()
        client.webSocket("$webSocketBaseUrl/speaking/voice-ws?token=$token&room_id=$roomId") {
            send(Frame.Text(json.encodeToString(VoiceTextTurnRequest(value = message, speed = speed))))
            for (frame in incoming) {
                if (frame !is Frame.Text) continue
                val event = json.decodeFromString<SpeakingStreamEvent>(frame.readText())
                when (event.type) {
                    "transcript" -> onTranscript(event.value.orEmpty())
                    "assistant_token" -> {
                        val value = event.value.orEmpty()
                        reply.append(value)
                        onToken(value)
                    }
                    "tts" -> {
                        if (reply.isEmpty() && !event.text.isNullOrBlank()) {
                            reply.append(event.text)
                        }
                    }
                    "done" -> break
                }
            }
        }
        return reply.toString().trim()
    }

    suspend fun streamVoiceAudioReply(
        token: String,
        roomId: String,
        chunks: List<VoiceAudioChunkDto>,
        transcriptHint: String? = null,
        speed: Float = 1f,
        onTranscript: (String) -> Unit = {},
        onToken: (String) -> Unit,
    ): String {
        val reply = StringBuilder()
        client.webSocket("$webSocketBaseUrl/speaking/voice-ws?token=$token&room_id=$roomId") {
            var committed = false
            for (frame in incoming) {
                if (frame !is Frame.Text) continue
                val event = json.decodeFromString<SpeakingStreamEvent>(frame.readText())
                when (event.type) {
                    "session_ready" -> {
                        if (!committed) {
                            chunks.forEach { chunk ->
                                send(Frame.Text(json.encodeToString(VoiceAudioChunkRequest(chunk.audioBase64, chunk.mimeType, chunk.transcript))))
                            }
                            send(Frame.Text(json.encodeToString(VoiceAudioCommitRequest(transcriptHint, speed))))
                            committed = true
                        }
                    }
                    "transcript" -> onTranscript(event.value.orEmpty())
                    "assistant_token" -> {
                        val value = event.value.orEmpty()
                        reply.append(value)
                        onToken(value)
                    }
                    "tts" -> {
                        if (reply.isEmpty() && !event.text.isNullOrBlank()) {
                            reply.append(event.text)
                        }
                    }
                    "done" -> break
                }
            }
        }
        return reply.toString().trim()
    }

    private val webSocketBaseUrl: String
        get() = when {
            baseUrl.startsWith("https://") -> baseUrl.replaceFirst("https://", "wss://")
            baseUrl.startsWith("http://") -> baseUrl.replaceFirst("http://", "ws://")
            else -> "ws://$baseUrl"
        }.trimEnd('/')
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
    @SerialName("current_level") val currentLevel: String = "Starter",
    @SerialName("target_level") val targetLevel: String = "B1",
    @SerialName("effort_level") val effortLevel: String = "Steady",
)

@Serializable
data class ProfileUpdateRequest(
    @SerialName("display_name") val displayName: String? = null,
    @SerialName("learning_vibe") val learningVibe: String? = null,
    @SerialName("active_language_code") val activeLanguageCode: String? = null,
    @SerialName("native_language_code") val nativeLanguageCode: String? = null,
    @SerialName("daily_vibe_minutes") val dailyVibeMinutes: Int? = null,
    @SerialName("ai_tone") val aiTone: String? = null,
    @SerialName("current_level") val currentLevel: String? = null,
    @SerialName("target_level") val targetLevel: String? = null,
    @SerialName("effort_level") val effortLevel: String? = null,
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
data class GrammarDropDto(
    val id: String,
    val title: String,
    val nudge: String,
    @SerialName("tiny_explanation") val tinyExplanation: String,
    val quests: List<String>,
)

@Serializable
data class GrammarExampleDto(
    val wrong: String? = null,
    val right: String,
    val note: String,
)

@Serializable
data class GrammarExerciseDto(
    val id: String,
    val type: String,
    val prompt: String,
    val options: List<String> = emptyList(),
    val explanation: String,
)

@Serializable
data class GrammarTopicDto(
    val id: String,
    val tag: String,
    val title: String,
    val level: String,
    val summary: String,
    @SerialName("micro_lesson") val microLesson: String,
    val rules: List<String>,
    val examples: List<GrammarExampleDto>,
    val exercises: List<GrammarExerciseDto>,
    val recommended: Boolean = false,
    val reason: String = "",
)

@Serializable
data class GrammarCheckRequest(
    @SerialName("topic_id") val topicId: String,
    @SerialName("exercise_id") val exerciseId: String,
    val answer: String,
)

@Serializable
data class GrammarCheckDto(
    val correct: Boolean,
    val expected: String,
    val feedback: String,
    @SerialName("score_delta") val scoreDelta: Int,
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
    val status: String = "learning",
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
data class SpeakingHistoryMessageDto(
    val id: Int,
    @SerialName("room_id") val roomId: String,
    val role: String,
    val content: String,
    @SerialName("created_at") val createdAt: String,
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

@Serializable
data class LearningPhraseDto(
    val phrase: String,
    val pronunciation: String = "",
    val meaning: String,
)

@Serializable
data class LearningVocabularyItemDto(
    val term: String,
    val pronunciation: String = "",
    val meaning: String,
)

@Serializable
data class LearningPracticeItemDto(
    val id: String,
    val prompt: String,
    val options: List<String>,
    @SerialName("correct_answer") val correctAnswer: String,
    val feedback: String,
)

@Serializable
data class LearningStepDto(
    val id: String,
    val title: String,
    val goal: String,
    @SerialName("teacher_note") val teacherNote: String,
    @SerialName("micro_task") val microTask: String,
    val examples: List<LearningPhraseDto>,
    val vocabulary: List<LearningVocabularyItemDto> = emptyList(),
    val practice: List<LearningPracticeItemDto> = emptyList(),
)

@Serializable
data class LearningDailyTaskDto(
    val id: String,
    val title: String,
    val detail: String,
    val action: String,
    val phrase: String = "",
    val minutes: Int = 3,
)

@Serializable
data class LearningPathDto(
    @SerialName("language_code") val languageCode: String,
    @SerialName("language_name") val languageName: String,
    val level: String,
    @SerialName("assistant_role") val assistantRole: String,
    @SerialName("next_room_prompt") val nextRoomPrompt: String,
    @SerialName("profile_summary") val profileSummary: String = "",
    @SerialName("coach_tip") val coachTip: String = "",
    @SerialName("review_prompt") val reviewPrompt: String = "",
    @SerialName("speaking_drill") val speakingDrill: String = "",
    val objectives: List<String> = emptyList(),
    @SerialName("daily_plan") val dailyPlan: List<LearningDailyTaskDto> = emptyList(),
    val steps: List<LearningStepDto>,
)

data class VoiceAudioChunkDto(
    val audioBase64: String,
    val mimeType: String = "audio/webm",
    val transcript: String? = null,
)

@Serializable
private data class SpeakingStreamEvent(
    val type: String,
    val value: String? = null,
    val text: String? = null,
    val provider: String? = null,
    val speed: Float? = null,
)

@Serializable
private data class VoiceTextTurnRequest(
    val type: String = "user_text",
    val value: String,
    val speed: Float = 1f,
)

@Serializable
private data class VoiceAudioChunkRequest(
    @SerialName("audio_base64") val audioBase64: String,
    @SerialName("mime_type") val mimeType: String,
    val transcript: String? = null,
    val type: String = "audio_chunk",
)

@Serializable
private data class VoiceAudioCommitRequest(
    val transcript: String? = null,
    val speed: Float = 1f,
    val type: String = "end_audio",
)
