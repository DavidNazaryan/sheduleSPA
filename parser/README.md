# Парсер расписания CACS SPA MSU для Android приложения

Этот парсер предназначен для получения расписания занятий с сайта https://cacs.spa.msu.ru/time-table/group?type=0 и может быть интегрирован в Android приложение.

## Структура проекта

```
parser/
├── __init__.py              # Экспорт основных классов
├── spa_client.py            # Низкоуровневый клиент для работы с сайтом
├── parse_html_schedule.py   # Парсинг HTML страницы с расписанием
├── api_client.py            # Высокоуровневый API клиент (рекомендуется для Android)
├── fastapi_server.py        # REST API сервер для интеграции
└── android_example.kt       # Пример использования в Android (Kotlin)
```

## Варианты интеграции в Android

### 1. Через REST API (Рекомендуется)

Запустите Python сервер с FastAPI:

```bash
pip install -r requirements.txt
python -m parser.fastapi_server
```

Сервер будет доступен на `http://localhost:8000` (или на вашем сервере).

#### Доступные эндпоинты:

- `GET /faculties` - Получить список факультетов
- `GET /courses?faculty_id={id}` - Получить курсы для факультета
- `GET /groups?faculty_id={id}&course={course}` - Получить группы
- `GET /schedule?faculty_id={id}&course={course}&group_id={gid}` - Получить расписание
- `GET /search?q={query}` - Поиск группы по названию

#### Пример запроса из Android:

```kotlin
val response = httpClient.newCall(
    Request.Builder()
        .url("http://your-server.com/api/schedule?faculty_id=5&course=1&group_id=1317")
        .build()
).execute()
```

Смотрите полный пример в файле `android_example.kt`.

### 2. Прямое использование Python кода (через Chaquopy)

Если вы используете [Chaquopy](https://chaquo.com/chaquopy/) для встроенного Python в Android:

```python
from parser.api_client import ScheduleApiClient

client = ScheduleApiClient()

# Получить факультеты
faculties = client.get_faculties()

# Получить расписание
schedule = client.get_schedule(
    faculty_id="5",
    course="1",
    group_id="1317"
)

if schedule.success:
    lessons = schedule.data["lessons"]
```

## Использование Python API

### Базовый пример

```python
from parser.api_client import ScheduleApiClient, to_json
import json

client = ScheduleApiClient()

# 1. Получить все факультеты
result = client.get_faculties()
print(result.data)  # [{'id': '5', 'name': 'Бакалавриат'}, ...]

# 2. Получить курсы для факультета
result = client.get_courses(faculty_id="5")
print(result.data)  # [{'id': '1', 'name': '1'}, {'id': '2', 'name': '2'}, ...]

# 3. Получить группы для факультета и курса
result = client.get_groups(faculty_id="5", course="1")
print(result.data)  # [{'id': '1317', 'name': '101гму'}, ...]

# 4. Получить расписание для группы
result = client.get_schedule(
    faculty_id="5",
    course="1",
    group_id="1317"
)
if result.success:
    print(f"Группа: {result.data['group']['name']}")
    print(f"Занятий: {len(result.data['lessons'])}")
    
    for lesson in result.data['lessons'][:3]:
        print(f"  {lesson['date']} {lesson['pair_number']} пара: {lesson['subject']}")

# 5. Поиск группы по названию
result = client.search_group("101")
print(result.data)  # Найденные группы
```

### С фильтром по датам

```python
result = client.get_schedule(
    faculty_id="5",
    course="1",
    group_id="1317",
    date_from="01.09.2025",
    date_to="30.09.2025"
)
```

### Получение JSON строки

```python
result = client.get_schedule("5", "1", "1317")
json_string = to_json(result)
# Отправьте json_string в Android приложение
```

## Формат данных

### Факультет/Курс/Группа

```json
{
  "id": "1317",
  "name": "101гму"
}
```

### Расписание

```json
{
  "success": true,
  "data": {
    "group": {
      "id": "1317",
      "name": "101гму"
    },
    "lessons": [
      {
        "id": "f5a1b26e96b0a7d8143573610776e778",
        "date": "18.05.2026",
        "pair_number": 1,
        "starts_at": "09:40",
        "ends_at": "11:10",
        "subject": "Английский язык",
        "type": "Пз",
        "teacher": "Депелян Рузанна Амбарцумовна",
        "room": "ауд. Г 608",
        "group_id": "2025_ГМУ-1-2",
        "notes": "Добавлено:  12.01.2026"
      }
    ]
  }
}
```

## Зависимости

```bash
pip install requests beautifulsoup4 fastapi uvicorn pydantic
```

Или используйте готовый `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Запуск REST API сервера

```bash
# development
python -m parser.fastapi_server

# или через uvicorn напрямую
uvicorn parser.fastapi_server:app --host 0.0.0.0 --port 8000 --reload
```

## Документация API

После запуска сервера откройте в браузере:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Примечания

1. Парсер использует session cookies и CSRF токены для работы с сайтом
2. Данные кэшируются в рамках одной сессии клиента
3. Для продакшена рекомендуется настроить проксирование через ваш бэкенд
4. Уважайте нагрузку на сервер cacs.spa.msu.ru - добавьте кэширование
