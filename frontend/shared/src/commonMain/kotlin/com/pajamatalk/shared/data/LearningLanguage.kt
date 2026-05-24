package com.pajamatalk.shared.data

data class LearningLanguage(
    val code: String,
    val label: String,
    val shortLabel: String,
    val flag: String,
    val sampleWord: String,
)

data class NativeLanguage(
    val code: String,
    val label: String,
    val shortLabel: String,
    val flag: String,
)

val SupportedLearningLanguages = listOf(
    LearningLanguage("en", "English", "EN", "🇬🇧", "cozy"),
    LearningLanguage("uk", "Ukrainian", "UK", "🇺🇦", "затишно"),
    LearningLanguage("ru", "Russian", "RU", "🇷🇺", "уютно"),
    LearningLanguage("sk", "Slovak", "SK", "🇸🇰", "ahoj"),
    LearningLanguage("pl", "Polish", "PL", "🇵🇱", "spoko"),
    LearningLanguage("cs", "Czech", "CZ", "🇨🇿", "pohoda"),
    LearningLanguage("fr", "French", "FR", "🇫🇷", "coucou"),
    LearningLanguage("es", "Spanish", "ES", "🇪🇸", "vale"),
    LearningLanguage("it", "Italian", "IT", "🇮🇹", "allora"),
    LearningLanguage("de", "German", "DE", "🇩🇪", "hallo"),
    LearningLanguage("pt", "Portuguese", "PT", "🇵🇹", "olá"),
    LearningLanguage("ko", "Korean", "KO", "🇰🇷", "안녕"),
    LearningLanguage("ja", "Japanese", "JA", "🇯🇵", "すごい"),
    LearningLanguage("zh", "Chinese", "ZH", "🇨🇳", "你好"),
    LearningLanguage("tr", "Turkish", "TR", "🇹🇷", "merhaba"),
)

val SupportedNativeLanguages = listOf(
    NativeLanguage("uk", "Ukrainian", "UK", "🇺🇦"),
    NativeLanguage("ru", "Russian", "RU", "🇷🇺"),
) + SupportedLearningLanguages
    .filterNot { it.code == "uk" || it.code == "ru" }
    .map { NativeLanguage(it.code, it.label, it.shortLabel, it.flag) }

fun languageByCode(code: String): LearningLanguage =
    SupportedLearningLanguages.firstOrNull { it.code == code } ?: SupportedLearningLanguages.first()

fun nativeLanguageByCode(code: String): NativeLanguage =
    SupportedNativeLanguages.firstOrNull { it.code == code } ?: SupportedNativeLanguages.first()
