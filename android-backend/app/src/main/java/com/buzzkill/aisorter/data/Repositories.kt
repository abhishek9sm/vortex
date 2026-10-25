package com.buzzkill.aisorter.data

import com.buzzkill.aisorter.model.Priority
import com.buzzkill.aisorter.model.RuleType
import kotlinx.coroutines.flow.Flow
import java.util.concurrent.TimeUnit

class NotificationRepository(private val dao: NotificationDao) {
    val notifications: Flow<List<NotificationEntity>> = dao.observeAll()
    val countsByPriority: Flow<List<PriorityCount>> = dao.observeCountsByPriority()
    val topApps: Flow<List<AppCount>> = dao.observeTopApps()

    fun observeByPriority(priority: Priority): Flow<List<NotificationEntity>> =
        dao.observeByPriority(priority)

    suspend fun save(notification: NotificationEntity) = dao.upsert(notification)
    suspend fun markRead(id: Long) = dao.markRead(id)
    suspend fun overridePriority(id: Long, priority: Priority) =
        dao.overridePriority(id, priority, "Priority changed manually.")
    suspend fun delete(id: Long) = dao.delete(id)
    suspend fun clearHistory() = dao.clearAll()

    suspend fun deleteOlderThan(days: Long) {
        require(days >= 0) { "days must not be negative" }
        val cutoff = System.currentTimeMillis() - TimeUnit.DAYS.toMillis(days)
        dao.deleteOlderThan(cutoff)
    }
}

class RuleRepository(private val dao: RuleDao) {
    val rules: Flow<List<RuleEntity>> = dao.observeAll()

    suspend fun enabledRules(): List<RuleEntity> = dao.getEnabled()

    suspend fun addRule(type: RuleType, value: String, priority: Priority) {
        val cleanValue = value.trim()
        require(cleanValue.isNotEmpty()) { "Rule value must not be blank." }
        dao.insert(
            RuleEntity(
                type = type,
                value = cleanValue,
                priority = priority,
            ),
        )
    }

    suspend fun toggleRule(rule: RuleEntity) {
        dao.update(rule.copy(enabled = !rule.enabled))
    }

    suspend fun deleteRule(id: Long) = dao.delete(id)

    suspend fun seedDefaultRulesIfEmpty() {
        if (dao.count() != 0) return
        val defaults = listOf(
            "otp",
            "verification code",
            "password",
            "urgent",
            "debited",
            "credited",
        ).map { RuleEntity(type = RuleType.KEYWORD, value = it, priority = Priority.HIGH) } +
            listOf("offer", "sale", "discount").map {
                RuleEntity(type = RuleType.KEYWORD, value = it, priority = Priority.LOW)
            }
        dao.insertAll(defaults)
    }
}
