package com.buzzkill.aisorter.ui

import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.app.NotificationManagerCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import com.buzzkill.aisorter.App
import com.buzzkill.aisorter.data.NotificationEntity
import com.buzzkill.aisorter.data.RuleEntity
import com.buzzkill.aisorter.model.ClassifiedBy
import com.buzzkill.aisorter.model.Priority
import com.buzzkill.aisorter.model.RuleType
import java.text.DateFormat
import java.util.Date

private val Accent = Color(0xFF6347E8)
private val HighColor = Color(0xFFC9474A)
private val MediumColor = Color(0xFFA66A0B)
private val LowColor = Color(0xFF23815A)
private val MutedColor = Color(0xFF777983)

class MainActivity : ComponentActivity() {
    private var notificationAccessEnabled by mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val container = (application as App).container
        val factory = MainViewModelFactory(
            container.notificationRepository,
            container.ruleRepository,
        )
        setContent {
            val darkTheme = androidx.compose.foundation.isSystemInDarkTheme()
            MaterialTheme(
                colorScheme = if (darkTheme) {
                    darkColorScheme(
                        primary = Color(0xFFA493FF),
                        background = Color(0xFF14151B),
                        surface = Color(0xFF1D1E26),
                    )
                } else {
                    lightColorScheme(
                        primary = Accent,
                        background = Color(0xFFF5F6FA),
                        surface = Color.White,
                    )
                },
            ) {
                val model: MainViewModel = viewModel(factory = factory)
                val notifications by model.notifications.collectAsState()
                val rules by model.rules.collectAsState()
                val counts by model.countsByPriority.collectAsState()
                val error by model.error.collectAsState()

                SorterDashboard(
                    notifications = notifications,
                    rules = rules,
                    counts = counts,
                    error = error,
                    notificationAccessEnabled = notificationAccessEnabled,
                    onOpenNotificationSettings = {
                        startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
                    },
                    onAddKeyword = model::addKeywordRule,
                    onToggleRule = model::toggleRule,
                    onDeleteRule = model::deleteRule,
                    onMarkRead = model::markRead,
                    onOverridePriority = model::overridePriority,
                    onClearHistory = model::clearHistory,
                )
            }
        }
    }

    override fun onResume() {
        super.onResume()
        notificationAccessEnabled =
            packageName in NotificationManagerCompat.getEnabledListenerPackages(this)
    }
}

@Composable
private fun SorterDashboard(
    notifications: List<NotificationEntity>,
    rules: List<RuleEntity>,
    counts: Map<Priority, Int>,
    error: String?,
    notificationAccessEnabled: Boolean,
    onOpenNotificationSettings: () -> Unit,
    onAddKeyword: (String, Priority) -> Unit,
    onToggleRule: (RuleEntity) -> Unit,
    onDeleteRule: (Long) -> Unit,
    onMarkRead: (Long) -> Unit,
    onOverridePriority: (Long, Priority) -> Unit,
    onClearHistory: () -> Unit,
) {
    var selectedPriority by rememberSaveable { mutableStateOf(Priority.HIGH.name) }
    var keyword by rememberSaveable { mutableStateOf("") }
    var showClearConfirmation by rememberSaveable { mutableStateOf(false) }
    val selected = Priority.valueOf(selectedPriority)
    val existingKeywords = rules
        .filter { it.type == RuleType.KEYWORD }
        .map { it.value.trim().lowercase() }
    val canAddKeyword = keyword.isNotBlank() &&
        keyword.trim().lowercase() !in existingKeywords
    val sortedNotifications = notifications.sortedWith(
        compareByDescending<NotificationEntity> { it.priority == selected }
            .thenByDescending { it.priority.weight }
            .thenByDescending { it.postTime },
    )

    if (showClearConfirmation) {
        AlertDialog(
            onDismissRequest = { showClearConfirmation = false },
            title = { Text("Clear notification history?") },
            text = { Text("This removes all saved notifications from this device.") },
            confirmButton = {
                TextButton(
                    onClick = {
                        onClearHistory()
                        showClearConfirmation = false
                    },
                ) {
                    Text("Clear history")
                }
            },
            dismissButton = {
                TextButton(onClick = { showClearConfirmation = false }) {
                    Text("Cancel")
                }
            },
        )
    }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background,
    ) {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(
                start = 18.dp,
                top = 12.dp,
                end = 18.dp,
                bottom = 28.dp,
            ),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Surface(
                            shape = RoundedCornerShape(11.dp),
                            color = Accent,
                            modifier = Modifier.size(34.dp),
                        ) {
                            Text(
                                "b.",
                                modifier = Modifier.padding(start = 8.dp, top = 2.dp),
                                color = Color.White,
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold,
                            )
                        }
                        Text(
                            "BuzzKill",
                            modifier = Modifier.padding(start = 10.dp),
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Surface(
                            shape = CircleShape,
                            color = if (notificationAccessEnabled) Color(0xFF56BC85) else MutedColor,
                            modifier = Modifier.size(8.dp),
                        ) {}
                        Text(
                            if (notificationAccessEnabled) " ACCESS ON" else " ACCESS OFF",
                            modifier = Modifier.padding(start = 6.dp),
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }

            item {
                Card(
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surface,
                    ),
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Eyebrow("YOUR ATTENTION, BACK IN YOUR HANDS")
                        Text(
                            "Less noise.\nMore signal.",
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold,
                            lineHeight = MaterialTheme.typography.headlineMedium.lineHeight,
                        )
                        Text(
                            "Your notifications, sorted on this device. Set rules and keep the important things in view.",
                            modifier = Modifier.padding(top = 8.dp),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }

            if (!notificationAccessEnabled) {
                item {
                    Card(
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFF0EDFF)),
                        shape = RoundedCornerShape(12.dp),
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                        ) {
                            Text(
                                "Connect your notifications",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.SemiBold,
                                color = Accent,
                            )
                            Text(
                                "Allow notification access to start sorting notifications from your apps.",
                                modifier = Modifier.padding(top = 4.dp),
                                style = MaterialTheme.typography.bodySmall,
                            )
                            Button(
                                onClick = onOpenNotificationSettings,
                                modifier = Modifier.padding(top = 10.dp),
                            ) {
                                Text("Open notification settings")
                            }
                        }
                    }
                }
            }

            if (error != null) {
                item {
                    Text(
                        error,
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(
                                color = Color(0xFFFFF0EF),
                                shape = RoundedCornerShape(10.dp),
                            )
                            .padding(12.dp),
                        color = HighColor,
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }

            item {
                Column(verticalArrangement = Arrangement.spacedBy(9.dp)) {
                    Eyebrow("01 / YOUR INBOX")
                    Text(
                        "Notifications  ·  ${notifications.size}",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Priority.entries.sortedByDescending { it.weight }.forEach { priority ->
                            PriorityCount(priority, counts[priority] ?: 0, Modifier.weight(1f))
                        }
                    }
                    Text(
                        "Show selected priority first",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                        Priority.entries.sortedByDescending { it.weight }.forEach { priority ->
                            FilterChip(
                                selected = selected == priority,
                                onClick = { selectedPriority = priority.name },
                                label = { Text(priority.name) },
                            )
                        }
                    }
                }
            }

            if (sortedNotifications.isEmpty()) {
                item {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.surface,
                        ),
                        shape = RoundedCornerShape(12.dp),
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(20.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                        ) {
                            Text(
                                "Your inbox is quiet",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold,
                            )
                            Text(
                                if (notificationAccessEnabled) {
                                    "Notifications from other apps will appear here as they arrive."
                                } else {
                                    "Enable notification access to see sorted notifications here."
                                },
                                modifier = Modifier.padding(top = 5.dp),
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                style = MaterialTheme.typography.bodySmall,
                            )
                        }
                    }
                }
            } else {
                items(sortedNotifications, key = { it.id }) { notification ->
                    NotificationCard(
                        notification = notification,
                        onMarkRead = { onMarkRead(notification.id) },
                        onOverridePriority = { priority ->
                            onOverridePriority(notification.id, priority)
                        },
                    )
                }
                item {
                    OutlinedButton(
                        onClick = { showClearConfirmation = true },
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text("Clear history")
                    }
                }
            }

            item {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surface,
                    ),
                    shape = RoundedCornerShape(14.dp),
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        Eyebrow("02 / PRIORITY RULES")
                        Text(
                            "Priority keywords",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold,
                        )
                        Text(
                            "Matching a keyword raises a notification to HIGH.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                        OutlinedTextField(
                            value = keyword,
                            onValueChange = { keyword = it },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true,
                            label = { Text("Add a keyword") },
                        )
                        Button(
                            onClick = {
                                onAddKeyword(keyword.trim(), Priority.HIGH)
                                keyword = ""
                            },
                            enabled = canAddKeyword,
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text("Add priority keyword")
                        }
                        if (rules.isEmpty()) {
                            Text(
                                "No rules yet.",
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                style = MaterialTheme.typography.bodySmall,
                            )
                        } else {
                            rules.forEach { rule ->
                                RuleRow(
                                    rule = rule,
                                    onToggle = { onToggleRule(rule) },
                                    onDelete = { onDeleteRule(rule.id) },
                                )
                            }
                        }
                    }
                }
            }

            item {
                Text(
                    "BUZZKILL  /  LOCAL-FIRST NOTIFICATION SORTER",
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 2.dp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.labelSmall,
                )
            }
        }
    }
}

@Composable
private fun PriorityCount(priority: Priority, count: Int, modifier: Modifier = Modifier) {
    val tint = priorityColor(priority)
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(11.dp),
        colors = CardDefaults.cardColors(
            containerColor = tint.copy(alpha = 0.09f),
        ),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 11.dp, horizontal = 10.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                count.toString(),
                color = tint,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                priority.name,
                color = tint,
                style = MaterialTheme.typography.labelSmall,
            )
        }
    }
}

@Composable
private fun NotificationCard(
    notification: NotificationEntity,
    onMarkRead: () -> Unit,
    onOverridePriority: (Priority) -> Unit,
) {
    var showPriorityOptions by rememberSaveable(notification.id) { mutableStateOf(false) }
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
    ) {
        Column(
            modifier = Modifier.padding(15.dp),
            verticalArrangement = Arrangement.spacedBy(7.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    notification.appName,
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    notification.priority.name,
                    modifier = Modifier
                        .background(
                            priorityColor(notification.priority).copy(alpha = 0.11f),
                            RoundedCornerShape(20.dp),
                        )
                        .padding(horizontal = 9.dp, vertical = 4.dp),
                    color = priorityColor(notification.priority),
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold,
                )
            }
            Text(
                notification.title ?: if (notification.isRedacted) {
                    "Content hidden"
                } else {
                    "Untitled notification"
                },
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
            )
            if (!notification.text.isNullOrBlank()) {
                Text(
                    notification.text,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Text(
                notification.reason,
                style = MaterialTheme.typography.bodySmall,
                color = Accent,
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    "${sourceLabel(notification.source)} · ${DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.SHORT).format(Date(notification.postTime))}",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (!notification.isRead) {
                        TextButton(onClick = onMarkRead) {
                            Text("Mark read")
                        }
                    } else {
                        Text(
                            "READ",
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            style = MaterialTheme.typography.labelSmall,
                        )
                    }
                    TextButton(onClick = { showPriorityOptions = !showPriorityOptions }) {
                        Text("Priority")
                    }
                }
            }
            if (showPriorityOptions) {
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Priority.entries.sortedByDescending { it.weight }.forEach { priority ->
                        FilterChip(
                            selected = notification.priority == priority,
                            onClick = {
                                onOverridePriority(priority)
                                showPriorityOptions = false
                            },
                            label = { Text(priority.name) },
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun RuleRow(
    rule: RuleEntity,
    onToggle: () -> Unit,
    onDelete: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                MaterialTheme.colorScheme.background,
                RoundedCornerShape(10.dp),
            )
            .padding(start = 10.dp, end = 4.dp, top = 6.dp, bottom = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                rule.value,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
            )
            Text(
                "${if (rule.type == RuleType.APP) "APP" else "KEYWORD"} · ${rule.priority.name}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        Switch(checked = rule.enabled, onCheckedChange = { onToggle() })
        TextButton(onClick = onDelete) {
            Text("Remove")
        }
    }
}

@Composable
private fun Eyebrow(text: String) {
    Text(
        text,
        color = Accent,
        style = MaterialTheme.typography.labelSmall,
        fontWeight = FontWeight.SemiBold,
        letterSpacing = 1.sp,
    )
}

private fun priorityColor(priority: Priority): Color = when (priority) {
    Priority.HIGH -> HighColor
    Priority.MEDIUM -> MediumColor
    Priority.LOW -> LowColor
}

private fun sourceLabel(source: ClassifiedBy): String = when (source) {
    ClassifiedBy.RULE -> "RULE"
    ClassifiedBy.AI -> "AI"
    ClassifiedBy.FALLBACK -> "FALLBACK"
}
