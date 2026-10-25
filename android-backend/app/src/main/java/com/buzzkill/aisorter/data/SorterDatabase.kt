package com.buzzkill.aisorter.data

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters

@Database(
    entities = [NotificationEntity::class, RuleEntity::class],
    version = 1,
    exportSchema = false,
)
@TypeConverters(Converters::class)
abstract class SorterDatabase : RoomDatabase() {
    abstract fun notificationDao(): NotificationDao
    abstract fun ruleDao(): RuleDao
}
