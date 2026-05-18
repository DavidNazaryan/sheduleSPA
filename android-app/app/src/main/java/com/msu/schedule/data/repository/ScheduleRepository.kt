package com.msu.schedule.data.repository

import com.msu.schedule.data.model.ApiResult
import com.msu.schedule.data.model.Course
import com.msu.schedule.data.model.Faculty
import com.msu.schedule.data.model.Group
import com.msu.schedule.data.model.Schedule
import com.msu.schedule.data.model.Lesson
import com.msu.schedule.data.remote.ScheduleParser
import com.msu.schedule.data.remote.SelectOption
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Репозиторий для работы с расписанием
 * Использует прямой парсинг сайта cacs.spa.msu.ru без промежуточных серверов
 */
@Singleton
class ScheduleRepository @Inject constructor(
    private val parser: ScheduleParser
) {
    
    /**
     * Получение списка факультетов
     */
    suspend fun getFaculties(): ApiResult<List<Faculty>> = withContext(Dispatchers.IO) {
        try {
            val options = parser.getFaculties()
            val faculties = options.map { option ->
                Faculty(id = option.value, name = option.label)
            }
            
            if (faculties.isNotEmpty()) {
                ApiResult.Success(faculties)
            } else {
                // Если не удалось распарсить, возвращаем пустой список с информацией
                ApiResult.Success(emptyList())
            }
        } catch (e: Exception) {
            ApiResult.Error("Ошибка загрузки факультетов: ${e.localizedMessage}", e)
        }
    }
    
    /**
     * Получение списка курсов для факультета
     */
    suspend fun getCourses(facultyId: String): ApiResult<List<Course>> = withContext(Dispatchers.IO) {
        try {
            val options = parser.getCourses(facultyId)
            val courses = options.map { option ->
                Course(id = option.value, name = option.label, facultyId = facultyId)
            }
            
            ApiResult.Success(courses)
        } catch (e: Exception) {
            ApiResult.Error("Ошибка загрузки курсов: ${e.localizedMessage}", e)
        }
    }
    
    /**
     * Получение списка групп для курса
     */
    suspend fun getGroups(facultyId: String, courseId: String): ApiResult<List<Group>> = withContext(Dispatchers.IO) {
        try {
            val options = parser.getGroups(facultyId, courseId)
            val groups = options.map { option ->
                Group(
                    id = option.value, 
                    name = option.label,
                    facultyId = facultyId,
                    courseId = courseId
                )
            }
            
            ApiResult.Success(groups)
        } catch (e: Exception) {
            ApiResult.Error("Ошибка загрузки групп: ${e.localizedMessage}", e)
        }
    }
    
    /**
     * Получение расписания для группы
     */
    suspend fun getSchedule(
        facultyId: String, 
        courseId: String, 
        groupId: String
    ): ApiResult<Schedule> = withContext(Dispatchers.IO) {
        try {
            val scheduleData = parser.getSchedule(facultyId, courseId, groupId)
            
            if (scheduleData.error != null) {
                ApiResult.Error(scheduleData.error)
            } else {
                val lessons = scheduleData.lessons.map { lesson ->
                    Lesson(
                        day = lesson.day,
                        date = lesson.date,
                        time = lesson.time,
                        subject = lesson.subject,
                        type = lesson.type,
                        teacher = lesson.teacher,
                        room = lesson.room
                    )
                }
                
                val schedule = Schedule(
                    groupId = groupId,
                    lessons = lessons
                )
                
                ApiResult.Success(schedule)
            }
        } catch (e: Exception) {
            ApiResult.Error("Ошибка загрузки расписания: ${e.localizedMessage}", e)
        }
    }
    
    /**
     * Поиск группы по названию
     */
    suspend fun searchGroup(name: String): ApiResult<List<Group>> = withContext(Dispatchers.IO) {
        try {
            val results = parser.searchGroups(name)
            val groups = results.map { result ->
                Group(
                    id = result.id,
                    name = result.name,
                    facultyId = "",
                    courseId = ""
                )
            }
            
            ApiResult.Success(groups)
        } catch (e: Exception) {
            ApiResult.Error("Ошибка поиска группы: ${e.localizedMessage}", e)
        }
    }
}
