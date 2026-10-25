package com.buzzkill.aisorter

import android.app.Application
import androidx.room.Room
import com.buzzkill.aisorter.data.NotificationRepository
import com.buzzkill.aisorter.data.RuleRepository
import com.buzzkill.aisorter.data.SorterDatabase
import com.buzzkill.aisorter.domain.HeuristicClassifier
import com.buzzkill.aisorter.domain.NotificationClassifier
import com.buzzkill.aisorter.domain.NotificationProcessor
import com.buzzkill.aisorter.domain.RuleEngine

class App : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}

class AppContainer(application: Application) {
    val database: SorterDatabase = Room.databaseBuilder(
        application,
        SorterDatabase::class.java,
        "ai-notification-sorter.db",
    ).build()

    val notificationRepository = NotificationRepository(database.notificationDao())
    val ruleRepository = RuleRepository(database.ruleDao())

    // TODO(SLM): Replace this binding with the on-device classifier implementation.
    private val classifier: NotificationClassifier = HeuristicClassifier()

    val processor = NotificationProcessor(
        rules = ruleRepository,
        notifications = notificationRepository,
        ruleEngine = RuleEngine(),
        classifier = classifier,
    )
}
