package com.buzzkill.aisorter.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.buzzkill.aisorter.data.NotificationEntity
import com.buzzkill.aisorter.data.NotificationRepository
import com.buzzkill.aisorter.data.RuleEntity
import com.buzzkill.aisorter.data.RuleRepository
import com.buzzkill.aisorter.model.Priority
import com.buzzkill.aisorter.model.RuleType
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

/**
 * The frontend-facing API. Keep Android notification objects out of this interface.
 */
class MainViewModel(
    private val notificationsRepository: NotificationRepository,
    private val rulesRepository: RuleRepository,
) : ViewModel() {
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    val notifications: StateFlow<List<NotificationEntity>> =
        notificationsRepository.notifications.stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5_000),
            emptyList(),
        )

    val rules: StateFlow<List<RuleEntity>> = rulesRepository.rules.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5_000),
        emptyList(),
    )

    val countsByPriority: StateFlow<Map<Priority, Int>> =
        notificationsRepository.countsByPriority
            .map { rows -> Priority.entries.associateWith { priority ->
                rows.firstOrNull { it.priority == priority }?.count ?: 0
            } }
            .stateIn(
                viewModelScope,
                SharingStarted.WhileSubscribed(5_000),
                Priority.entries.associateWith { 0 },
            )

    init {
        runAction { rulesRepository.seedDefaultRulesIfEmpty() }
    }

    fun addKeywordRule(value: String, priority: Priority) =
        addRule(RuleType.KEYWORD, value, priority)

    fun addAppRule(packageName: String, priority: Priority) =
        addRule(RuleType.APP, packageName, priority)

    private fun addRule(type: RuleType, value: String, priority: Priority) {
        runAction {
            rulesRepository.addRule(type, value, priority)
        }
    }

    fun toggleRule(rule: RuleEntity) {
        runAction { rulesRepository.toggleRule(rule) }
    }

    fun deleteRule(id: Long) {
        runAction { rulesRepository.deleteRule(id) }
    }

    fun markRead(id: Long) {
        runAction { notificationsRepository.markRead(id) }
    }

    fun overridePriority(id: Long, priority: Priority) {
        runAction { notificationsRepository.overridePriority(id, priority) }
    }

    fun clearHistory() {
        runAction { notificationsRepository.clearHistory() }
    }

    private fun runAction(action: suspend () -> Unit) {
        viewModelScope.launch {
            _error.value = null
            try {
                action()
            } catch (error: CancellationException) {
                throw error
            } catch (error: Exception) {
                _error.value = error.message ?: "The requested change could not be saved."
            }
        }
    }
}

class MainViewModelFactory(
    private val notificationsRepository: NotificationRepository,
    private val rulesRepository: RuleRepository,
) : androidx.lifecycle.ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        require(modelClass.isAssignableFrom(MainViewModel::class.java))
        return MainViewModel(notificationsRepository, rulesRepository) as T
    }
}
