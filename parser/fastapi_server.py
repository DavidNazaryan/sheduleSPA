"""FastAPI REST server for Android app integration."""
from __future__ import annotations

import json
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .api_client import ScheduleApiClient, ApiResult, to_json

app = FastAPI(
    title="CACS SPA MSU Schedule API",
    description="REST API для получения расписания занятий с cacs.spa.msu.ru",
    version="1.0.0"
)

# Разрешить CORS для мобильных приложений
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_api_client = ScheduleApiClient()


class ApiResponse(BaseModel):
    success: bool
    data: dict | list | None = None
    error: str | None = None


@app.get("/", tags=["root"])
def root():
    """Информация об API."""
    return {
        "name": "CACS SPA MSU Schedule API",
        "version": "1.0.0",
        "endpoints": {
            "/faculties": "Получить список факультетов",
            "/courses": "Получить список курсов для факультета",
            "/groups": "Получить список групп для факультета и курса",
            "/schedule": "Получить расписание для группы",
            "/search": "Поиск группы по названию",
        }
    }


@app.get("/faculties", response_model=ApiResponse, tags=["faculties"])
def get_faculties():
    """
    Получить список всех факультетов.
    
    Возвращает массив объектов с полями:
    - id: идентификатор факультета
    - name: название факультета
    """
    result = _api_client.get_faculties()
    return ApiResponse(success=result.success, data=result.data, error=result.error)


@app.get("/courses", response_model=ApiResponse, tags=["courses"])
def get_courses(faculty_id: str = Query(..., description="ID факультета")):
    """
    Получить список курсов для указанного факультета.
    
    Параметры:
    - faculty_id: ID факультета (из /faculties)
    
    Возвращает массив объектов с полями:
    - id: идентификатор курса
    - name: название курса
    """
    result = _api_client.get_courses(faculty_id)
    return ApiResponse(success=result.success, data=result.data, error=result.error)


@app.get("/groups", response_model=ApiResponse, tags=["groups"])
def get_groups(
    faculty_id: str = Query(..., description="ID факультета"),
    course: str = Query(..., description="ID курса")
):
    """
    Получить список групп для указанного факультета и курса.
    
    Параметры:
    - faculty_id: ID факультета (из /faculties)
    - course: ID курса (из /courses)
    
    Возвращает массив объектов с полями:
    - id: идентификатор группы
    - name: название группы
    """
    result = _api_client.get_groups(faculty_id, course)
    return ApiResponse(success=result.success, data=result.data, error=result.error)


@app.get("/schedule", response_model=ApiResponse, tags=["schedule"])
def get_schedule(
    faculty_id: str = Query(..., description="ID факультета"),
    course: str = Query(..., description="ID курса"),
    group_id: str = Query(..., description="ID группы"),
    date_from: Optional[str] = Query(None, description="Дата начала в формате DD.MM.YYYY"),
    date_to: Optional[str] = Query(None, description="Дата окончания в формате DD.MM.YYYY")
):
    """
    Получить расписание для указанной группы.
    
    Параметры:
    - faculty_id: ID факультета (из /faculties)
    - course: ID курса (из /courses)
    - group_id: ID группы (из /groups)
    - date_from: необязательно, дата начала периода (DD.MM.YYYY)
    - date_to: необязательно, дата окончания периода (DD.MM.YYYY)
    
    Возвращает объект с полями:
    - group: информация о группе (id, name)
    - lessons: массив занятий со следующими полями:
        - id: уникальный идентификатор занятия
        - date: дата в формате DD.MM.YYYY
        - pair_number: номер пары
        - starts_at: время начала
        - ends_at: время окончания
        - subject: название предмета
        - type: тип занятия (Лекция, Практика и т.д.)
        - teacher: преподаватель
        - room: аудитория
        - group_id: ID группы
        - notes: примечания
    """
    result = _api_client.get_schedule(
        faculty_id=faculty_id,
        course=course,
        group_id=group_id,
        date_from=date_from,
        date_to=date_to
    )
    return ApiResponse(success=result.success, data=result.data, error=result.error)


@app.get("/search", response_model=ApiResponse, tags=["search"])
def search_group(q: str = Query(..., description="Поисковый запрос")):
    """
    Поиск группы по названию.
    
    Параметры:
    - q: подстрока для поиска (регистронезависимый поиск)
    
    Возвращает массив найденных групп с полями:
    - id: идентификатор группы
    - name: название группы
    - faculty_id: ID факультета
    - faculty_name: название факультета
    - course: ID курса
    - course_name: название курса
    """
    result = _api_client.search_group(q)
    return ApiResponse(success=result.success, data=result.data, error=result.error)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
