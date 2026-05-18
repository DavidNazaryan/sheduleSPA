package com.msu.schedule.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.msu.schedule.data.model.Faculty
import com.msu.schedule.data.model.Group
import com.msu.schedule.data.model.Lesson
import com.msu.schedule.data.model.Schedule
import com.msu.schedule.ui.theme.MSUBlue
import com.msu.schedule.ui.viewmodel.ScheduleViewModel
import com.msu.schedule.ui.viewmodel.ScheduleUiState

@Composable
fun ScheduleScreen(
    viewModel: ScheduleViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Расписание МГУ") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MSUBlue,
                    titleContentColor = Color.White
                )
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            if (uiState.isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
            } else if (uiState.error != null) {
                ErrorView(
                    message = uiState.error!!,
                    onRetry = { viewModel.clearError() }
                )
            } else {
                ScheduleContent(
                    uiState = uiState,
                    onFacultySelected = { viewModel.selectFaculty(it) },
                    onCourseSelected = { viewModel.selectCourse(it) },
                    onGroupSelected = { viewModel.selectGroup(it) }
                )
            }
        }
    }
}

@Composable
private fun ScheduleContent(
    uiState: ScheduleUiState,
    onFacultySelected: (String) -> Unit,
    onCourseSelected: (String) -> Unit,
    onGroupSelected: (String) -> Unit
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Факультет
        item {
            Text(
                text = "Выберите факультет",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            FacultySelector(
                faculties = uiState.faculties,
                selectedId = uiState.selectedFacultyId,
                onSelected = onFacultySelected
            )
        }
        
        // Курс
        if (uiState.selectedFacultyId != null) {
            item {
                Text(
                    text = "Выберите курс",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                CourseSelector(
                    courses = uiState.courses,
                    selectedId = uiState.selectedCourseId,
                    onSelected = onCourseSelected
                )
            }
        }
        
        // Группа
        if (uiState.selectedCourseId != null) {
            item {
                Text(
                    text = "Выберите группу",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                GroupSelector(
                    groups = uiState.groups,
                    selectedId = uiState.selectedGroupId,
                    onSelected = onGroupSelected
                )
            }
        }
        
        // Расписание
        if (uiState.schedule != null) {
            item {
                ScheduleList(schedule = uiState.schedule!!)
            }
        }
    }
}

@Composable
private fun FacultySelector(
    faculties: List<Faculty>,
    selectedId: String?,
    onSelected: (String) -> Unit
) {
    if (faculties.isEmpty()) {
        Text(
            text = "Загрузка факультетов...",
            style = MaterialTheme.typography.bodyMedium,
            color = Color.Gray
        )
        return
    }
    
    faculties.forEach { faculty ->
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { onSelected(faculty.id) }
                .padding(vertical = 4.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (faculty.id == selectedId) MSUBlue else Color.White
            )
        ) {
            Text(
                text = faculty.name,
                modifier = Modifier.padding(12.dp),
                color = if (faculty.id == selectedId) Color.White else Color.Black
            )
        }
    }
}

@Composable
private fun CourseSelector(
    courses: List<com.msu.schedule.data.model.Course>,
    selectedId: String?,
    onSelected: (String) -> Unit
) {
    courses.forEach { course ->
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { onSelected(course.id) }
                .padding(vertical = 4.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (course.id == selectedId) MSUBlue else Color.White
            )
        ) {
            Text(
                text = course.name,
                modifier = Modifier.padding(12.dp),
                color = if (course.id == selectedId) Color.White else Color.Black
            )
        }
    }
}

@Composable
private fun GroupSelector(
    groups: List<Group>,
    selectedId: String?,
    onSelected: (String) -> Unit
) {
    groups.forEach { group ->
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { onSelected(group.id) }
                .padding(vertical = 4.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (group.id == selectedId) MSUBlue else Color.White
            )
        ) {
            Text(
                text = group.name,
                modifier = Modifier.padding(12.dp),
                color = if (group.id == selectedId) Color.White else Color.Black
            )
        }
    }
}

@Composable
private fun ScheduleList(schedule: Schedule) {
    if (schedule.lessons.isEmpty()) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Text(
                text = "Нет занятий",
                modifier = Modifier.padding(16.dp),
                style = MaterialTheme.typography.bodyMedium,
                color = Color.Gray
            )
        }
        return
    }
    
    // Группируем занятия по дням
    val lessonsByDay = schedule.lessons.groupBy { it.day }
    
    lessonsByDay.forEach { (day, lessons) ->
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = day.ifEmpty { "Расписание" },
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = MSUBlue
                )
                Spacer(modifier = Modifier.height(12.dp))
                
                lessons.forEachIndexed { index, lesson ->
                    LessonItem(lesson = lesson)
                    if (index < lessons.lastIndex) {
                        Divider(modifier = Modifier.padding(vertical = 8.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun LessonItem(lesson: Lesson) {
    Column(
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = lesson.time.ifEmpty { "--:--" },
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold,
                color = MSUBlue
            )
            Text(
                text = lesson.room.ifEmpty { lesson.audience }.ifEmpty { "?" },
                style = MaterialTheme.typography.labelMedium,
                color = Color.Gray
            )
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = lesson.subject.ifEmpty { "Не указано" },
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold
        )
        val typeAndTeacher = buildString {
            if (lesson.type.isNotEmpty()) append(lesson.type)
            if (lesson.type.isNotEmpty() && lesson.teacher.isNotEmpty()) append(" • ")
            if (lesson.teacher.isNotEmpty()) append(lesson.teacher)
        }
        if (typeAndTeacher.isNotEmpty()) {
            Text(
                text = typeAndTeacher,
                style = MaterialTheme.typography.bodySmall,
                color = Color.Gray
            )
        }
    }
}

@Composable
private fun ErrorView(
    message: String,
    onRetry: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Ошибка",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.error
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            color = Color.Gray
        )
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onRetry) {
            Text("Повторить")
        }
    }
}
