package com.msu.schedule.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.msu.schedule.data.model.ApiResult
import com.msu.schedule.data.model.Course
import com.msu.schedule.data.model.Faculty
import com.msu.schedule.data.model.Group
import com.msu.schedule.data.model.Schedule
import com.msu.schedule.data.repository.ScheduleRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ScheduleUiState(
    val faculties: List<Faculty> = emptyList(),
    val courses: List<Course> = emptyList(),
    val groups: List<Group> = emptyList(),
    val schedule: Schedule? = null,
    val selectedFacultyId: String? = null,
    val selectedCourseId: String? = null,
    val selectedGroupId: String? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class ScheduleViewModel @Inject constructor(
    private val repository: ScheduleRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(ScheduleUiState())
    val uiState: StateFlow<ScheduleUiState> = _uiState.asStateFlow()
    
    init {
        loadFaculties()
    }
    
    fun loadFaculties() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            when (val result = repository.getFaculties()) {
                is ApiResult.Success -> {
                    _uiState.value = _uiState.value.copy(
                        faculties = result.data,
                        isLoading = false
                    )
                }
                is ApiResult.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = result.message
                    )
                }
                else -> {}
            }
        }
    }
    
    fun selectFaculty(facultyId: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(
                selectedFacultyId = facultyId,
                isLoading = true,
                courses = emptyList(),
                groups = emptyList(),
                schedule = null
            )
            when (val result = repository.getCourses(facultyId)) {
                is ApiResult.Success -> {
                    _uiState.value = _uiState.value.copy(
                        courses = result.data,
                        isLoading = false
                    )
                }
                is ApiResult.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = result.message
                    )
                }
                else -> {}
            }
        }
    }
    
    fun selectCourse(courseId: String) {
        viewModelScope.launch {
            val facultyId = _uiState.value.selectedFacultyId ?: return@launch
            _uiState.value = _uiState.value.copy(
                selectedCourseId = courseId,
                isLoading = true,
                groups = emptyList(),
                schedule = null
            )
            when (val result = repository.getGroups(facultyId, courseId)) {
                is ApiResult.Success -> {
                    _uiState.value = _uiState.value.copy(
                        groups = result.data,
                        isLoading = false
                    )
                }
                is ApiResult.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = result.message
                    )
                }
                else -> {}
            }
        }
    }
    
    fun selectGroup(groupId: String) {
        viewModelScope.launch {
            val facultyId = _uiState.value.selectedFacultyId ?: return@launch
            val courseId = _uiState.value.selectedCourseId ?: return@launch
            
            _uiState.value = _uiState.value.copy(
                selectedGroupId = groupId,
                isLoading = true,
                schedule = null
            )
            when (val result = repository.getSchedule(facultyId, courseId, groupId)) {
                is ApiResult.Success -> {
                    _uiState.value = _uiState.value.copy(
                        schedule = result.data,
                        isLoading = false
                    )
                }
                is ApiResult.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = result.message
                    )
                }
                else -> {}
            }
        }
    }
    
    fun searchGroup(query: String) {
        if (query.length < 2) return
        
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            when (val result = repository.searchGroup(query)) {
                is ApiResult.Success -> {
                    _uiState.value = _uiState.value.copy(
                        groups = result.data,
                        isLoading = false
                    )
                }
                is ApiResult.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = result.message
                    )
                }
                else -> {}
            }
        }
    }
    
    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
