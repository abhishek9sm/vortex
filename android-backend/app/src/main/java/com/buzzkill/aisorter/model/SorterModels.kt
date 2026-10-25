package com.buzzkill.aisorter.model

enum class Priority(val weight: Int) {
    LOW(1),
    MEDIUM(2),
    HIGH(3),
}

enum class RuleType {
    APP,
    KEYWORD,
}

enum class ClassifiedBy {
    RULE,
    AI,
    FALLBACK,
}

/**
 * Platform-independent notification input shared with the SLM integration.
 */
data class NotificationData(
    val sbnKey: String,
    val packageName: String,
    val appName: String,
    val title: String?,
    val text: String?,
    val postTime: Long,
    val isRedacted: Boolean,
) {
    val searchableText: String
        get() = listOfNotNull(title, text)
            .joinToString(separator = " ")
            .lowercase()
}

data class ClassificationResult(
    val priority: Priority,
    val reason: String,
    val source: ClassifiedBy,
)
