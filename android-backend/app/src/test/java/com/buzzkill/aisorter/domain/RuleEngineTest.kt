package com.buzzkill.aisorter.domain

import com.buzzkill.aisorter.data.RuleEntity
import com.buzzkill.aisorter.model.ClassifiedBy
import com.buzzkill.aisorter.model.NotificationData
import com.buzzkill.aisorter.model.Priority
import com.buzzkill.aisorter.model.RuleType
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class RuleEngineTest {
    private val engine = RuleEngine()

    @Test
    fun keywordMatchIsCaseInsensitive() {
        val result = engine.evaluate(
            notification(text = "Your OTP is 123456"),
            listOf(rule(RuleType.KEYWORD, "otp", Priority.HIGH)),
        )

        assertEquals(Priority.HIGH, result?.priority)
        assertEquals(ClassifiedBy.RULE, result?.source)
    }

    @Test
    fun appRuleMatchesPackageName() {
        val result = engine.evaluate(
            notification(packageName = "com.example.mail"),
            listOf(rule(RuleType.APP, "com.example.mail", Priority.LOW)),
        )

        assertEquals(Priority.LOW, result?.priority)
    }

    @Test
    fun highestPriorityWinsAcrossMatches() {
        val result = engine.evaluate(
            notification(packageName = "com.example.bank", text = "Amount debited"),
            listOf(
                rule(RuleType.APP, "com.example.bank", Priority.LOW),
                rule(RuleType.KEYWORD, "debited", Priority.HIGH),
            ),
        )

        assertEquals(Priority.HIGH, result?.priority)
        assertEquals("Matched keyword rule: debited", result?.reason)
    }

    @Test
    fun disabledRuleIsIgnored() {
        val result = engine.evaluate(
            notification(text = "urgent"),
            listOf(rule(RuleType.KEYWORD, "urgent", Priority.HIGH, enabled = false)),
        )

        assertNull(result)
    }

    @Test
    fun noMatchReturnsNull() {
        assertNull(
            engine.evaluate(
                notification(text = "hello"),
                listOf(rule(RuleType.KEYWORD, "urgent", Priority.HIGH)),
            ),
        )
    }

    @Test
    fun nullAndRedactedContentDoesNotCrash() {
        val result = engine.evaluate(
            notification(title = null, text = null, isRedacted = true),
            listOf(rule(RuleType.KEYWORD, "otp", Priority.HIGH)),
        )

        assertNull(result)
    }

    private fun notification(
        packageName: String = "com.example.app",
        title: String? = "Notice",
        text: String? = null,
        isRedacted: Boolean = false,
    ) = NotificationData(
        sbnKey = "test-key",
        packageName = packageName,
        appName = "Example",
        title = title,
        text = text,
        postTime = 1L,
        isRedacted = isRedacted,
    )

    private fun rule(
        type: RuleType,
        value: String,
        priority: Priority,
        enabled: Boolean = true,
    ) = RuleEntity(
        type = type,
        value = value,
        priority = priority,
        enabled = enabled,
    )
}
