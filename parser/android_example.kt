// Пример использования парсера в Android приложении (Kotlin)
// Этот файл демонстрирует, как можно интегрировать парсер расписания
// через REST API или напрямую используя Python скрипт

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject

/**
 * Модель данных для расписания занятий
 */
data class Lesson(
    val id: String,
    val date: String,
    val pairNumber: Int,
    val startsAt: String,
    val endsAt: String,
    val subject: String?,
    val type: String?,
    val teacher: String?,
    val room: String?,
    val groupId: String?,
    val notes: String?
)

data class GroupInfo(
    val id: String,
    val name: String
)

data class ScheduleResponse(
    val group: GroupInfo,
    val lessons: List<Lesson>
)

data class ApiResult(
    val success: Boolean,
    val data: Any?,
    val error: String?
)

/**
 * Клиент для работы с расписанием CACS SPA MSU
 * 
 * Варианты интеграции:
 * 1. Через REST API (рекомендуется) - запустить Python сервер с FastAPI
 * 2. Через Chaquopy - встроенный Python в Android
 * 3. Через отдельный бэкенд-сервис
 */
class ScheduleApiClient {
    
    private val httpClient = OkHttpClient()
    
    // URL вашего Python REST API сервера
    private val baseUrl = "http://your-server.com/api"
    
    /**
     * Получить список факультетов
     */
    suspend fun getFaculties(): ApiResult = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/faculties")
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@withContext ApiResult(false, null, "HTTP ${response.code}")
                }
                
                val json = JSONObject(response.body?.string() ?: "")
                ApiResult(true, json, null)
            }
        } catch (e: Exception) {
            Log.e("ScheduleAPI", "Error fetching faculties", e)
            ApiResult(false, null, e.message)
        }
    }
    
    /**
     * Получить список курсов для факультета
     */
    suspend fun getCourses(facultyId: String): ApiResult = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/courses?faculty_id=$facultyId")
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@withContext ApiResult(false, null, "HTTP ${response.code}")
                }
                
                val json = JSONObject(response.body?.string() ?: "")
                ApiResult(true, json, null)
            }
        } catch (e: Exception) {
            Log.e("ScheduleAPI", "Error fetching courses", e)
            ApiResult(false, null, e.message)
        }
    }
    
    /**
     * Получить список групп для факультета и курса
     */
    suspend fun getGroups(facultyId: String, course: String): ApiResult = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/groups?faculty_id=$facultyId&course=$course")
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@withContext ApiResult(false, null, "HTTP ${response.code}")
                }
                
                val json = JSONObject(response.body?.string() ?: "")
                ApiResult(true, json, null)
            }
        } catch (e: Exception) {
            Log.e("ScheduleAPI", "Error fetching groups", e)
            ApiResult(false, null, e.message)
        }
    }
    
    /**
     * Получить расписание для группы
     */
    suspend fun getSchedule(
        facultyId: String,
        course: String,
        groupId: String,
        dateFrom: String? = null,
        dateTo: String? = null
    ): ApiResult = withContext(Dispatchers.IO) {
        try {
            val urlBuilder = StringBuilder("$baseUrl/schedule?")
                .append("faculty_id=$facultyId&")
                .append("course=$course&")
                .append("group_id=$groupId")
            
            if (dateFrom != null) {
                urlBuilder.append("&date_from=$dateFrom")
            }
            if (dateTo != null) {
                urlBuilder.append("&date_to=$dateTo")
            }
            
            val request = Request.Builder()
                .url(urlBuilder.toString())
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@withContext ApiResult(false, null, "HTTP ${response.code}")
                }
                
                val jsonString = response.body?.string() ?: ""
                val json = JSONObject(jsonString)
                
                if (json.getBoolean("success")) {
                    val data = json.getJSONObject("data")
                    val schedule = parseScheduleResponse(data)
                    ApiResult(true, schedule, null)
                } else {
                    ApiResult(false, null, json.getString("error"))
                }
            }
        } catch (e: Exception) {
            Log.e("ScheduleAPI", "Error fetching schedule", e)
            ApiResult(false, null, e.message)
        }
    }
    
    /**
     * Поиск группы по названию
     */
    suspend fun searchGroup(query: String): ApiResult = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/search?q=$query")
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@withContext ApiResult(false, null, "HTTP ${response.code}")
                }
                
                val json = JSONObject(response.body?.string() ?: "")
                ApiResult(true, json, null)
            }
        } catch (e: Exception) {
            Log.e("ScheduleAPI", "Error searching groups", e)
            ApiResult(false, null, e.message)
        }
    }
    
    private fun parseScheduleResponse(data: JSONObject): ScheduleResponse {
        val groupJson = data.getJSONObject("group")
        val group = GroupInfo(
            id = groupJson.getString("id"),
            name = groupJson.getString("name")
        )
        
        val lessonsJson = data.getJSONArray("lessons")
        val lessons = mutableListOf<Lesson>()
        
        for (i in 0 until lessonsJson.length()) {
            val lessonJson = lessonsJson.getJSONObject(i)
            lessons.add(
                Lesson(
                    id = lessonJson.optString("id", ""),
                    date = lessonJson.optString("date", ""),
                    pairNumber = lessonJson.optInt("pair_number", 0),
                    startsAt = lessonJson.optString("starts_at", ""),
                    endsAt = lessonJson.optString("ends_at", ""),
                    subject = lessonJson.optString("subject", null),
                    type = lessonJson.optString("type", null),
                    teacher = lessonJson.optString("teacher", null),
                    room = lessonJson.optString("room", null),
                    groupId = lessonJson.optString("group_id", null),
                    notes = lessonJson.optString("notes", null)
                )
            )
        }
        
        return ScheduleResponse(group, lessons)
    }
}

/**
 * Пример использования в ViewModel
 */
/*
class ScheduleViewModel : ViewModel() {
    
    private val apiClient = ScheduleApiClient()
    
    private val _faculties = MutableLiveData<JSONArray>()
    val faculties: LiveData<JSONArray> = _faculties
    
    private val _schedule = MutableLiveData<ScheduleResponse>()
    val schedule: LiveData<ScheduleResponse> = _schedule
    
    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading
    
    fun loadFaculties() {
        viewModelScope.launch {
            _loading.value = true
            val result = apiClient.getFaculties()
            _loading.value = false
            
            if (result.success) {
                _faculties.value = result.data as? JSONArray
            } else {
                // Показать ошибку
            }
        }
    }
    
    fun loadSchedule(facultyId: String, course: String, groupId: String) {
        viewModelScope.launch {
            _loading.value = true
            val result = apiClient.getSchedule(facultyId, course, groupId)
            _loading.value = false
            
            if (result.success) {
                _schedule.value = result.data as? ScheduleResponse
            } else {
                // Показать ошибку
            }
        }
    }
}
*/
