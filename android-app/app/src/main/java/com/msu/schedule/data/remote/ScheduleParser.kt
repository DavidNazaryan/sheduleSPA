package com.msu.schedule.data.remote

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.jsoup.Jsoup
import org.jsoup.nodes.Document
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Парсер расписания МГУ, работающий напрямую с сайтом cacs.spa.msu.ru
 * Не требует промежуточного сервера - все запросы идут напрямую к сайту
 */
@Singleton
class ScheduleParser @Inject constructor() {
    
    companion object {
        private const val BASE_URL = "https://cacs.spa.msu.ru"
        private const val TIME_TABLE_URL = "$BASE_URL/time-table/group"
        private const val SEARCH_URL = "$BASE_URL/api/search"
    }
    
    /**
     * Получение HTML страницы с расписанием
     */
    private suspend fun fetchHtml(url: String): Document = withContext(Dispatchers.IO) {
        Jsoup.connect(url)
            .userAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            .timeout(15000)
            .followRedirects(true)
            .get()
    }
    
    /**
     * Поиск группы по названию
     * Возвращает список найденных групп с их ID и названиями
     */
    suspend fun searchGroups(query: String): List<GroupSearchResult> = withContext(Dispatchers.IO) {
        try {
            // Пробуем получить страницу поиска или главную страницу для извлечения данных
            val doc = fetchHtml("$BASE_URL/time-table/group")
            
            // Ищем группы в выпадающих списках или скриптах страницы
            val results = mutableListOf<GroupSearchResult>()
            
            // Парсим возможные варианты групп из HTML
            // Обычно данные хранятся в data-attributes или в JSON внутри скриптов
            doc.select("option[value]").forEach { option ->
                val groupName = option.text().trim()
                if (groupName.contains(query, ignoreCase = true)) {
                    val groupId = option.attr("value")
                    if (groupId.isNotEmpty()) {
                        results.add(GroupSearchResult(groupId, groupName))
                    }
                }
            }
            
            // Если не нашли в option, пробуем искать в других элементах
            if (results.isEmpty()) {
                doc.select("[data-group], .group-item, a[href*='group']").forEach { element ->
                    val name = element.text().trim()
                    if (name.contains(query, ignoreCase = true)) {
                        val id = element.attr("data-group").ifEmpty { 
                            element.attr("href").substringAfter("group=").substringBefore("&")
                        }
                        if (id.isNotEmpty()) {
                            results.add(GroupSearchResult(id, name))
                        }
                    }
                }
            }
            
            results.distinctBy { it.id }
        } catch (e: Exception) {
            e.printStackTrace()
            emptyList()
        }
    }
    
    /**
     * Получение расписания для конкретной группы
     * @param facultyId ID факультета
     * @param courseId ID курса
     * @param groupId ID группы
     */
    suspend fun getSchedule(facultyId: String, courseId: String, groupId: String): ScheduleData {
        return withContext(Dispatchers.IO) {
            try {
                val url = buildString {
                    append(TIME_TABLE_URL)
                    append("?type=0") // type=0 для групп
                    if (facultyId.isNotEmpty()) append("&faculty=$facultyId")
                    if (courseId.isNotEmpty()) append("&course=$courseId")
                    if (groupId.isNotEmpty()) append("&group=$groupId")
                }
                
                val doc = fetchHtml(url)
                parseScheduleFromDocument(doc)
            } catch (e: Exception) {
                e.printStackTrace()
                ScheduleData(emptyList(), "Ошибка загрузки: ${e.message}")
            }
        }
    }
    
    /**
     * Парсинг документа HTML в структуру данных расписания
     */
    private fun parseScheduleFromDocument(doc: Document): ScheduleData {
        val lessons = mutableListOf<Lesson>()
        var errorMessage: String? = null
        
        // Ищем таблицу или контейнер с расписанием
        val scheduleContainer = doc.selectFirst(".timetable, .schedule-table, table") 
            ?: doc.selectFirst("div[class*='schedule'], div[class*='timetable']")
        
        if (scheduleContainer == null) {
            // Пробуем найти дни недели и занятия другими способами
            return parseAlternativeSchedule(doc)
        }
        
        // Парсим дни недели
        doc.select(".day, .schedule-day, tr.day-row").forEach { dayElement ->
            val dayName = dayElement.selectFirst(".day-name, h3, td:first-child")?.text()?.trim() ?: "Неизвестно"
            val dateStr = dayElement.selectFirst(".date, .day-date")?.text()?.trim()
            
            // Парсим занятия внутри дня
            dayElement.select(".lesson, .pair, tr.lesson-row, td:not(.day-name)").forEach { lessonElement ->
                val time = lessonElement.selectFirst(".time, .pair-time")?.text()?.trim()
                val subject = lessonElement.selectFirst(".subject, .discipline")?.text()?.trim()
                val type = lessonElement.selectFirst(".type, .lesson-type")?.text()?.trim()
                val teacher = lessonElement.selectFirst(".teacher, .professor")?.text()?.trim()
                val room = lessonElement.selectFirst(".room, .audience, .classroom")?.text()?.trim()
                
                if (!subject.isNullOrBlank()) {
                    lessons.add(
                        Lesson(
                            day = dayName,
                            date = dateStr,
                            time = time ?: "",
                            subject = subject,
                            type = type ?: "",
                            teacher = teacher ?: "",
                            room = room ?: ""
                        )
                    )
                }
            }
        }
        
        return ScheduleData(lessons, errorMessage)
    }
    
    /**
     * Альтернативный парсинг если стандартная структура не найдена
     */
    private fun parseAlternativeSchedule(doc: Document): ScheduleData {
        val lessons = mutableListOf<Lesson>()
        
        // Пробуем найти любые элементы содержащие информацию о занятиях
        doc.select("td, div").forEach { element ->
            val text = element.text().trim()
            if (text.contains(":") || text.matches(Regex("\\d{2}:\\d{2}"))) {
                // Это может быть время занятия
                val parent = element.parent()
                val allText = parent?.text() ?: text
                
                lessons.add(
                    Lesson(
                        day = "",
                        date = "",
                        time = text.substringBefore("-").trim(),
                        subject = allText.substringAfter(text).take(100),
                        type = "",
                        teacher = "",
                        room = ""
                    )
                )
            }
        }
        
        return ScheduleData(lessons, null)
    }
    
    /**
     * Получение списка факультетов (если доступно на странице)
     */
    suspend fun getFaculties(): List<SelectOption> = withContext(Dispatchers.IO) {
        try {
            val doc = fetchHtml("$BASE_URL/time-table/group")
            val options = mutableListOf<SelectOption>()
            
            doc.select("select[name='faculty'] option, #faculty-select option").forEach { option ->
                val value = option.attr("value")
                val text = option.text().trim()
                if (value.isNotEmpty() && text.isNotEmpty()) {
                    options.add(SelectOption(value, text))
                }
            }
            
            options
        } catch (e: Exception) {
            e.printStackTrace()
            emptyList()
        }
    }
    
    /**
     * Получение списка курсов для выбранного факультета
     */
    suspend fun getCourses(facultyId: String): List<SelectOption> = withContext(Dispatchers.IO) {
        try {
            val url = "$TIME_TABLE_URL?type=0&faculty=$facultyId"
            val doc = fetchHtml(url)
            val options = mutableListOf<SelectOption>()
            
            doc.select("select[name='course'] option, #course-select option").forEach { option ->
                val value = option.attr("value")
                val text = option.text().trim()
                if (value.isNotEmpty() && text.isNotEmpty()) {
                    options.add(SelectOption(value, text))
                }
            }
            
            options
        } catch (e: Exception) {
            e.printStackTrace()
            emptyList()
        }
    }
    
    /**
     * Получение списка групп для выбранного курса
     */
    suspend fun getGroups(facultyId: String, courseId: String): List<SelectOption> = withContext(Dispatchers.IO) {
        try {
            val url = "$TIME_TABLE_URL?type=0&faculty=$facultyId&course=$courseId"
            val doc = fetchHtml(url)
            val options = mutableListOf<SelectOption>()
            
            doc.select("select[name='group'] option, #group-select option").forEach { option ->
                val value = option.attr("value")
                val text = option.text().trim()
                if (value.isNotEmpty() && text.isNotEmpty()) {
                    options.add(SelectOption(value, text))
                }
            }
            
            options
        } catch (e: Exception) {
            e.printStackTrace()
            emptyList()
        }
    }
}

// Модели данных
data class ScheduleData(
    val lessons: List<Lesson>,
    val error: String? = null
)

data class Lesson(
    val day: String,
    val date: String,
    val time: String,
    val subject: String,
    val type: String,
    val teacher: String,
    val room: String
)

data class SelectOption(
    val value: String,
    val label: String
)

data class GroupSearchResult(
    val id: String,
    val name: String
)
