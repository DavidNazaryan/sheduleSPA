package com.msu.schedule.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Faculty(
    val id: String,
    val name: String
)

@Serializable
data class Course(
    val id: String,
    val name: String,
    val facultyId: String = ""
)

@Serializable
data class Group(
    val id: String,
    val name: String,
    val facultyId: String = "",
    val courseId: String = ""
)

@Serializable
data class Schedule(
    val groupId: String,
    val lessons: List<Lesson>
)

@Serializable
data class Lesson(
    @SerialName("day") val day: String = "",
    @SerialName("date") val date: String = "",
    @SerialName("time") val time: String = "",
    @SerialName("subject") val subject: String = "",
    @SerialName("type") val type: String = "",
    @SerialName("teacher") val teacher: String = "",
    @SerialName("room") val room: String = "",
    @SerialName("audience") val audience: String = ""
)

sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val message: String, val exception: Throwable? = null) : ApiResult<Nothing>()
    object Loading : ApiResult<Nothing>()
}
