package com.buzzkill.aisorter.domain

import com.buzzkill.aisorter.model.ClassifiedBy
import com.buzzkill.aisorter.model.ClassificationResult
import com.buzzkill.aisorter.model.NotificationData
import com.buzzkill.aisorter.model.Priority

/**
 * SLM integration seam. The model implementation must process only local input.
 */
interface NotificationClassifier {
    suspend fun classify(n: NotificationData): ClassificationResult
}

class HeuristicClassifier : NotificationClassifier {
    override suspend fun classify(n: NotificationData): ClassificationResult {
        val content = n.searchableText
        val priority = when {
            listOf("otp", "verification code", "password", "urgent", "emergency")
                .any { content.contains(it) } -> Priority.HIGH
            content.isBlank() || n.isRedacted -> Priority.MEDIUM
            listOf("sale", "offer", "discount", "promotion")
                .any { content.contains(it) } -> Priority.LOW
            else -> Priority.MEDIUM
        }
        return ClassificationResult(
            priority = priority,
            reason = "Local heuristic classification (replace with on-device AI).",
            source = ClassifiedBy.AI,
        )
    }
}
