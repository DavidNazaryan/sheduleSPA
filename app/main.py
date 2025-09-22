from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from parser.spa_client import OptionItem, SpaScheduleClient

app = FastAPI(title="MSU Schedule Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")


class OptionResponse(BaseModel):
    id: str
    name: str


class GroupInfo(BaseModel):
    id: str
    name: Optional[str] = None


class Lesson(BaseModel):
    id: str
    date: str
    pair_number: Optional[int] = None
    starts_at: Optional[str] = None
    ends_at: Optional[str] = None
    subject: Optional[str] = None
    type: Optional[str] = None
    teacher: Optional[str] = None
    room: Optional[str] = None
    group_id: Optional[str] = None
    notes: Optional[str] = None


class ScheduleResponse(BaseModel):
    group: GroupInfo
    lessons: List[Lesson]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/options/faculties", response_model=List[OptionResponse])
async def list_faculties() -> List[OptionResponse]:
    client = SpaScheduleClient()
    faculties = client.list_faculties()
    return _serialize_options(faculties)


@app.get("/api/options/courses", response_model=List[OptionResponse])
async def list_courses(faculty_id: str = Query(..., alias="faculty")) -> List[OptionResponse]:
    client = SpaScheduleClient()
    courses = client.list_courses(faculty_id)
    return _serialize_options(courses)


@app.get("/api/options/groups", response_model=List[OptionResponse])
async def list_groups(
    faculty_id: str = Query(..., alias="faculty"),
    course: str = Query(...),
) -> List[OptionResponse]:
    client = SpaScheduleClient()
    groups = client.list_groups(faculty_id, course)
    return _serialize_options(groups)


@app.get("/api/schedule", response_model=ScheduleResponse)
async def get_schedule(
    faculty_id: str = Query(..., alias="faculty"),
    course: str = Query(...),
    group_id: str = Query(..., alias="group"),
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
) -> ScheduleResponse:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="'from' date must be before 'to' date")

    client = SpaScheduleClient()
    result = client.fetch_schedule(
        faculty_id=faculty_id,
        course=course,
        group_id=group_id,
        date_from=date_from,
        date_to=date_to,
    )
    group_name = result["group"].get("name") if result.get("group") else None
    lessons = [Lesson(**lesson) for lesson in result.get("lessons", [])]
    return ScheduleResponse(group=GroupInfo(id=group_id, name=group_name), lessons=lessons)


def _serialize_options(items: List[OptionItem]) -> List[OptionResponse]:
    return [OptionResponse(id=item.id, name=item.name) for item in items]
