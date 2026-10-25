package com.buzzkill.aisorter.domain

import com.buzzkill.aisorter.data.NotificationEntity
import com.buzzkill.aisorter.data.NotificationRepository
import com.buzzkill.aisorter.data.RuleRepository
import com.buzzkill.aisorter.model.ClassifiedBy
import com.buzzkill.aisorter.model.ClassificationResult
import com.buzzkill.aisorter.model.NotificationData
import com.buzzkill.aisorter.model.Priority
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.withTimeout

class NotificationProcessor(
    private val rules: RuleRepository,
    private val notifications: NotificationRepository,
    private val ruleEngine: RuleEngine,
    private val classifier: NotificationClassifier,
) {
    suspend fun process(notification: NotificationData) {
        rules.seedDefaultRulesIfEmpty()
        val result = ruleEngine.evaluate(notification, rules.enabledRules())
            ?: classifySafely(notification)

        notifications.save(
            NotificationEntity(
                sbnKey = notification.sbnKey,
                packageName = notification.packageName,
                appName = notification.appName,
                title = notification.title,
                text = notification.text,
                postTime = notification.postTime,
                priority = result.priority,
                reason = result.reason,
                source = result.source,
                isRedacted = notification.isRedacted,
            ),
        )
    }

    private suspend fun classifySafely(notification: NotificationData): ClassificationResult =
        try {
            withTimeout(CLASSIFICATION_TIMEOUT_MILLIS) {
                classifier.classify(notification)
            }
        } catch (error: TimeoutCancellationException) {
            fallback("On-device AI timed out; assigned medium priority.")
        } catch (error: CancellationException) {
            throw error
        } catch (error: Exception) {
            fallback("On-device AI failed; assigned medium priority.")
        }

    private fun fallback(reason: String) = ClassificationResult(
        priority = Priority.MEDIUM,
        reason = reason,
        source = ClassifiedBy.FALLBACK,
    )

    private companion object {
        const val CLASSIFICATION_TIMEOUT_MILLIS = 3_000L
    }
}
