package com.buzzkill.aisorter.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.buzzkill.aisorter.model.Priority
import kotlinx.coroutines.flow.Flow

@Dao
interface NotificationDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(notification: NotificationEntity)

    @Query("SELECT * FROM notifications ORDER BY postTime DESC")
    fun observeAll(): Flow<List<NotificationEntity>>

    @Query("SELECT * FROM notifications WHERE priority = :priority ORDER BY postTime DESC")
    fun observeByPriority(priority: Priority): Flow<List<NotificationEntity>>

    @Query(
        """
        SELECT priority, COUNT(*) AS count
        FROM notifications
        GROUP BY priority
        """,
    )
    fun observeCountsByPriority(): Flow<List<PriorityCount>>

    @Query(
        """
        SELECT packageName, appName, COUNT(*) AS count
        FROM notifications
        GROUP BY packageName, appName
        ORDER BY count DESC
        """,
    )
    fun observeTopApps(): Flow<List<AppCount>>

    @Query("UPDATE notifications SET isRead = 1 WHERE id = :id")
    suspend fun markRead(id: Long)

    @Query("UPDATE notifications SET priority = :priority, reason = :reason WHERE id = :id")
    suspend fun overridePriority(id: Long, priority: Priority, reason: String)

    @Query("DELETE FROM notifications WHERE id = :id")
    suspend fun delete(id: Long)

    @Query("DELETE FROM notifications")
    suspend fun clearAll()

    @Query("DELETE FROM notifications WHERE postTime < :cutoffMillis")
    suspend fun deleteOlderThan(cutoffMillis: Long)
}
