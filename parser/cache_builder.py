from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import calendar
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from parser.spa_client import SpaScheduleClient  # noqa: E402

CACHE_PATH = BASE_DIR / "data" / "cache.json"
DEFAULT_DAYS = 7


@dataclass
class GroupSchedule:
    faculty_id: str
    faculty_name: str
    course_id: str
    course_name: str
    group_id: str
    group_name: str
    date_from: date
    date_to: date
    lessons: List[dict]


def _shift_months(base: date, months: int) -> date:
    """Return a date shifted by a number of calendar months.

    If the target month has fewer days than the base day, clamp to the last day
    of the target month.
    """
    year = base.year + (base.month - 1 + months) // 12
    month = (base.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(base.day, last_day)
    return date(year, month, day)


def daterange(days: int = DEFAULT_DAYS) -> tuple[date, date]:
    # Required period: from 2 months before today to 6 months after today
    today = date.today()
    start = _shift_months(today, -2)
    end = _shift_months(today, 6)
    return start, end


def build_cache(days: int = DEFAULT_DAYS) -> tuple[Dict[str, GroupSchedule], List[dict]]:
    client = SpaScheduleClient()
    start, end = daterange(days)
    groups_data: Dict[str, GroupSchedule] = {}
    options_tree: List[dict] = []

    faculties = client.list_faculties()
    for faculty in faculties:
        faculty_entry = {"id": faculty.id, "name": faculty.name, "courses": []}
        options_tree.append(faculty_entry)

        courses = client.list_courses(faculty.id)
        for course in courses:
            course_entry = {"id": course.id, "name": course.name, "groups": []}
            faculty_entry["courses"].append(course_entry)

            groups = client.list_groups(faculty.id, course.id)
            for group in groups:
                course_entry["groups"].append({"id": group.id, "name": group.name})
                try:
                    result = client.fetch_schedule(
                        faculty_id=faculty.id,
                        course=course.id,
                        group_id=group.id,
                        date_from=start,
                        date_to=end,
                    )
                    lessons = result.get("lessons", [])
                except Exception as exc:  # noqa: BLE001
                    print(
                        f"Failed to fetch schedule for {faculty.name} / {course.name} / {group.name}: {exc}"
                    )
                    lessons = []
                groups_data[group.id] = GroupSchedule(
                    faculty_id=faculty.id,
                    faculty_name=faculty.name,
                    course_id=course.id,
                    course_name=course.name,
                    group_id=group.id,
                    group_name=group.name,
                    date_from=start,
                    date_to=end,
                    lessons=lessons,
                )
    return groups_data, options_tree


def dump_cache(
    cache: Dict[str, GroupSchedule],
    options_tree: List[dict],
    path: Path = CACHE_PATH,
) -> None:
    generated_at = datetime.utcnow().isoformat() + "Z"
    payload = {
        "generated_at": generated_at,
        "date_from": next(iter(cache.values())).date_from.isoformat() if cache else None,
        "date_to": next(iter(cache.values())).date_to.isoformat() if cache else None,
        "options": {
            "generated_at": generated_at,
            "faculties": options_tree,
        },
        "groups": {
            group_id: {
                "faculty_id": entry.faculty_id,
                "faculty_name": entry.faculty_name,
                "course_id": entry.course_id,
                "course_name": entry.course_name,
                "group_id": entry.group_id,
                "group_name": entry.group_name,
                "date_from": entry.date_from.isoformat(),
                "date_to": entry.date_to.isoformat(),
                "lessons": entry.lessons,
            }
            for group_id, entry in cache.items()
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main(days: Optional[int] = None) -> None:
    period = days or DEFAULT_DAYS
    print(f"Building schedule cache for {period} days…")
    cache, options_tree = build_cache(period)
    dump_cache(cache, options_tree)
    print(f"Cache stored at {CACHE_PATH}")


if __name__ == "__main__":
    days_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(days_arg)
