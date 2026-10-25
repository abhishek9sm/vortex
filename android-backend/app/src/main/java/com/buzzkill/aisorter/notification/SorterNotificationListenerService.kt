package com.buzzkill.aisorter.notification

import android.app.Notification
import android.content.pm.PackageManager
import android.os.Build
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import com.buzzkill.aisorter.App
import com.buzzkill.aisorter.model.NotificationData
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

class SorterNotificationListenerService : NotificationListenerService() {
    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        if (sbn == null) return
        serviceScope.launch {
            try {
                if (shouldIgnore(sbn)) return@launch
                val packageName = sbn.packageName ?: return@launch
                val notification = sbn.notification ?: return@launch
                val extras = notification.extras
                val title = extras?.getCharSequence(Notification.EXTRA_TITLE)
                    ?.toString()
                    ?.takeIf(String::isNotBlank)
                val bigText = extras?.getCharSequence(Notification.EXTRA_BIG_TEXT)
                    ?.toString()
                    ?.takeIf(String::isNotBlank)
                val text = bigText
                    ?: extras?.getCharSequence(Notification.EXTRA_TEXT)
                        ?.toString()
                        ?.takeIf(String::isNotBlank)
                val appName = resolveAppName(packageName)
                val data = NotificationData(
                    sbnKey = sbn.key ?: return@launch,
                    packageName = packageName,
                    appName = appName,
                    title = title,
                    text = text,
                    postTime = sbn.postTime,
                    isRedacted = title == null && text == null,
                )
                (application as App).container.processor.process(data)
            } catch (error: Exception) {
                if (error is CancellationException) throw error
                Log.e(TAG, "Could not process posted notification.", error)
            }
        }
    }

    override fun onDestroy() {
        serviceScope.cancel()
        super.onDestroy()
    }

    private fun shouldIgnore(sbn: StatusBarNotification): Boolean {
        if (sbn.packageName == packageName) return true
        val flags = sbn.notification?.flags ?: return true
        if (flags and Notification.FLAG_GROUP_SUMMARY != 0) return true
        if (flags and Notification.FLAG_ONGOING_EVENT != 0) return true
        if (flags and Notification.FLAG_FOREGROUND_SERVICE != 0) return true
        return false
    }

    @Suppress("DEPRECATION")
    private fun resolveAppName(packageName: String): String =
        try {
            val applicationInfo = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                packageManager.getApplicationInfo(
                    packageName,
                    PackageManager.ApplicationInfoFlags.of(0),
                )
            } else {
                packageManager.getApplicationInfo(packageName, 0)
            }
            packageManager.getApplicationLabel(applicationInfo).toString()
        } catch (_: Exception) {
            packageName
        }

    private companion object {
        const val TAG = "SorterListener"
    }
}
