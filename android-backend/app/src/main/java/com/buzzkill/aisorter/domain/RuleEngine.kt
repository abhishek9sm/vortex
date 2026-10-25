package com.buzzkill.aisorter.domain

import com.buzzkill.aisorter.data.RuleEntity
import com.buzzkill.aisorter.model.ClassifiedBy
import com.buzzkill.aisorter.model.ClassificationResult
import com.buzzkill.aisorter.model.NotificationData
import com.buzzkill.aisorter.model.RuleType

class RuleEngine {
    fun evaluate(
        notification: NotificationData,
        rules: List<RuleEntity>,
    ): ClassificationResult? {
        val matchingRule = rules.asSequence()
            .filter { it.enabled }
            .filter { rule ->
                when (rule.type) {
                    RuleType.APP -> rule.value.equals(
                        notification.packageName,
                        ignoreCase = true,
                    )
                    RuleType.KEYWORD -> notification.searchableText.contains(
                        rule.value,
                        ignoreCase = true,
                    )
                }
            }
            .maxByOrNull { it.priority.weight }
            ?: return null

        val matchDescription = when (matchingRule.type) {
            RuleType.APP -> "Matched app rule: ${matchingRule.value}"
            RuleType.KEYWORD -> "Matched keyword rule: ${matchingRule.value}"
        }
        return ClassificationResult(
            priority = matchingRule.priority,
            reason = matchDescription,
            source = ClassifiedBy.RULE,
        )
    }
}
