package com.pajamatalk.shared.data

data class LearningLanguage(
    val code: String,
    val label: String,
    val shortLabel: String,
    val sampleWord: String,
)

val SupportedLearningLanguages = listOf(
    LearningLanguage("en", "English", "EN", "cozy"),
    LearningLanguage("sk", "Slovak", "SK", "ahoj"),
    LearningLanguage("pl", "Polish", "PL", "spoko"),
    LearningLanguage("cs", "Czech", "CS", "pohoda"),
    LearningLanguage("fr", "French", "FR", "coucou"),
    LearningLanguage("es", "Spanish", "ES", "vale"),
    LearningLanguage("it", "Italian", "IT", "allora"),
    LearningLanguage("ko", "Korean", "KO", "안녕"),
    LearningLanguage("ja", "Japanese", "JA", "すごい"),
    LearningLanguage("zh", "Chinese", "ZH", "你好"),
    LearningLanguage("tr", "Turkish", "TR", "merhaba"),
)

fun languageByCode(code: String): LearningLanguage =
    SupportedLearningLanguages.firstOrNull { it.code == code } ?: SupportedLearningLanguages.first()
