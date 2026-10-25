package com.buzzkill.aisorter.data

import androidx.room.TypeConverter
import com.buzzkill.aisorter.model.ClassifiedBy
import com.buzzkill.aisorter.model.Priority
import com.buzzkill.aisorter.model.RuleType

class Converters {
    @TypeConverter
    fun priorityFromString(value: String): Priority = Priority.valueOf(value)

    @TypeConverter
    fun priorityToString(value: Priority): String = value.name

    @TypeConverter
    fun ruleTypeFromString(value: String): RuleType = RuleType.valueOf(value)

    @TypeConverter
    fun ruleTypeToString(value: RuleType): String = value.name

    @TypeConverter
    fun classifiedByFromString(value: String): ClassifiedBy = ClassifiedBy.valueOf(value)

    @TypeConverter
    fun classifiedByToString(value: ClassifiedBy): String = value.name
}
