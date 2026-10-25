package com.buzzkill.aisorter.data

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import com.buzzkill.aisorter.model.ClassifiedBy
import com.buzzkill.aisorter.model.Priority
import com.buzzkill.aisorter.model.RuleType

@Entity(
    tableName = "notifications",
    indices = [
        Index(value = ["sbnKey"], unique = true),
        Index(value = ["priority", "postTime"]),
    ],
)
data class NotificationEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val sbnKey: String,
    val packageName: String,
    val appName: String,
    val title: String?,
    val text: String?,
    val postTime: Long,
    val priority: Priority,
    val reason: String,
    val source: ClassifiedBy,
    val isRedacted: Boolean,
    val isRead: Boolean = false,
)

@Entity(
    tableName = "rules",
    indices = [Index(value = ["type", "value"], unique = true)],
)
data class RuleEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val type: RuleType,
    val value: String,
    val priority: Priority,
    val enabled: Boolean = true,
)

data class PriorityCount(
    val priority: Priority,
    val count: Int,
)

data class AppCount(
    val packageName: String,
    val appName: String,
    val count: Int,
)
