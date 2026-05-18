# 📱 Расписание МГУ - Android Приложение

Нативное Android приложение для просмотра расписания занятий МГУ им. Ломоносова.

## ✨ Особенности

- **Прямое подключение к сайту** - приложение напрямую парсит сайт `https://cacs.spa.msu.ru` без промежуточных серверов
- **Не требуется backend** - все запросы идут напрямую к сайту расписания
- **Современный UI** - Material Design 3, Jetpack Compose
- **Архитектура MVVM** - чистая архитектура с разделением ответственности
- **Dependency Injection** - Hilt для внедрения зависимостей

## 🏗 Архитектура

```
app/
├── data/
│   ├── model/           # Модели данных (Lesson, Schedule, Faculty, Course, Group)
│   ├── remote/          # Парсер (ScheduleParser) - прямой парсинг сайта
│   └── repository/      # Репозиторий для бизнес-логики
├── di/                  # Dependency Injection (Hilt)
├── ui/
│   ├── screens/         # UI экраны на Jetpack Compose
│   ├── theme/           # Тема приложения (цвета, шрифты)
│   └── viewmodel/       # ViewModel для управления состоянием
└── MainActivity.kt
```

## 🔧 Технологии

| Технология | Назначение |
|------------|------------|
| **Kotlin** | Основной язык разработки |
| **Jetpack Compose** | Современный declarative UI |
| **Hilt** | Dependency injection |
| **OkHttp** | HTTP клиент для запросов |
| **Jsoup** | HTML парсинг сайта расписания |
| **Coroutines & Flow** | Асинхронность и реактивность |
| **Material 3** | Дизайн система Google |

## 🚀 Как это работает

### Прямой парсинг сайта

Приложение использует библиотеку **Jsoup** для прямого парсинга HTML страницы сайта расписания МГУ:

```kotlin
// ScheduleParser.kt
@Singleton
class ScheduleParser @Inject constructor() {
    
    companion object {
        private const val BASE_URL = "https://cacs.spa.msu.ru"
        private const val TIME_TABLE_URL = "$BASE_URL/time-table/group"
    }
    
    suspend fun getSchedule(facultyId: String, courseId: String, groupId: String): ScheduleData {
        val url = buildString {
            append(TIME_TABLE_URL)
            append("?type=0")
            if (facultyId.isNotEmpty()) append("&faculty=$facultyId")
            if (courseId.isNotEmpty()) append("&course=$courseId")
            if (groupId.isNotEmpty()) append("&group=$groupId")
        }
        
        // Прямой запрос к сайту без промежуточного сервера
        val doc = Jsoup.connect(url)
            .userAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...")
            .timeout(15000)
            .followRedirects(true)
            .get()
        
        return parseScheduleFromDocument(doc)
    }
}
```

### Поток данных

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ UI (Compose)│────▶│  ViewModel  │────▶│ Repository  │────▶│   Parser    │────▶│   Сайт      │
│             │◀────│             │◀────│             │◀────│ (Jsoup)     │◀────│ cacs.spa    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. **UI (Compose)** → Пользователь выбирает группу, запрашивает данные через ViewModel
2. **ViewModel** → Вызывает методы репозитория, управляет состоянием UI
3. **Repository** → Использует Parser для получения данных
4. **ScheduleParser** → Делает HTTP запрос напрямую к сайту и парсит HTML
5. **Данные** → Возвращаются обратно в UI для отображения

## 📦 Установка и запуск

### Требования

- Android Studio Hedgehog (2023.1.1) или новее
- JDK 17
- Android SDK 24+ (минимум), 34 (target)

### Шаги

1. **Откройте проект в Android Studio**
   ```
   File → Open → Выберите папку android-app
   ```

2. **Синхронизируйте Gradle**
   ```
   File → Sync Project with Gradle Files
   ```

3. **Запустите приложение**
   - На эмуляторе: выберите устройство и нажмите Run ▶️
   - На реальном устройстве: включите отладку по USB и подключите устройство

## 🔐 Разрешения

В `AndroidManifest.xml` уже добавлены необходимые разрешения:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

## 🎨 Использование

1. **Выберите факультет** из списка
2. **Выберите курс** (появится после выбора факультета)
3. **Выберите группу** (появится после выбора курса)
4. **Просмотрите расписание** - занятия сгруппированы по дням недели

Каждое занятие показывает:
- ⏰ Время проведения
- 📚 Название предмета
- 👨‍🏫 Преподавателя
- 🏛 Аудиторию
- 📝 Тип занятия (лекция/семинар)

## 📝 Структура данных

### Lesson (Занятие)
```kotlin
data class Lesson(
    val day: String,      // День недели
    val date: String,     // Дата
    val time: String,     // Время
    val subject: String,  // Предмет
    val type: String,     // Тип (лекция/семинар)
    val teacher: String,  // Преподаватель
    val room: String      // Аудитория
)
```

### Schedule (Расписание)
```kotlin
data class Schedule(
    val groupId: String,
    val lessons: List<Lesson>
)
```

## 🛠 Расширение функционала

### Добавление поддержки других сайтов

Для поддержки других сайтов расписания:

1. Создайте новый парсер в `data/remote/`
2. Обновите `ScheduleRepository` для работы с новым источником
3. Добавьте настройки выбора источника в UI

### Кэширование данных для офлайн режима

Для работы без интернета можно добавить Room database:

```kotlin
// 1. Добавить зависимость в build.gradle.kts
implementation("androidx.room:room-runtime:2.6.0")
ksp("androidx.room:room-compiler:2.6.0")

// 2. Создать Entity
@Entity(tableName = "lessons")
data class LessonEntity(
    @PrimaryKey val id: Int,
    val day: String,
    val time: String,
    val subject: String,
    // ...
)

// 3. Создать DAO
@Dao
interface LessonDao {
    @Query("SELECT * FROM lessons WHERE groupId = :groupId")
    fun getLessons(groupId: String): Flow<List<LessonEntity>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(lessons: List<LessonEntity>)
}
```

## ⚠️ Важные замечания

1. **Зависимость от сайта** - приложение зависит от доступности и структуры сайта `cacs.spa.msu.ru`
2. **Изменения в HTML** - при изменении структуры сайта потребуется обновить парсер в `ScheduleParser.kt`
3. **Сетевое соединение** - требуется интернет для загрузки актуального расписания
4. **Rate limiting** - парсер делает запросы только при действиях пользователя, не спамит запросами
5. **User-Agent** - установлен браузерный User-Agent для избежания блокировок

## 📄 Лицензия

Проект создан в образовательных целях.

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Контакты

Вопросы и предложения присылайте на почту или создавайте Issue в репозитории.

---

**Приложение не является официальным продуктом МГУ им. Ломоносова**
