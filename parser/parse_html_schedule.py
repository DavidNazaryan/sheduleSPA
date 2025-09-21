from __future__ import annotations

import hashlib
import json
import re
from datetime import date as Date, datetime
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple, Union

from bs4 import BeautifulSoup, Tag

HtmlSource = Union[str, bytes, Path]

_PAIR_RE = re.compile(r"(\d+)")
_TIME_RANGE_RE = re.compile(r"^(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})$")
_NOTE_PREFIXES = (
    "обнов",
    "перен",
    "замен",
    "примеч",
    "вним",
    "отмен",
    "добав",
)


def parse_html_schedule(
    html: HtmlSource,
    *,
    group_id: Optional[str] = None,
    date_from: Optional[Date] = None,
    date_to: Optional[Date] = None,
) -> List[dict[str, Any]]:
    """Parse the SPA timetable HTML page and return lesson dictionaries."""
    soup = BeautifulSoup(_ensure_html(html), "html.parser")
    table = soup.select_one("table#timeTable")
    if table is None:
        return []

    lessons: List[dict[str, Any]] = []
    current_dates: List[str] = []

    for row in table.find_all("tr"):
        day_header = row.find("th", class_="headday")
        if day_header:
            current_dates = [th.get_text(strip=True) for th in row.select("th.headdate")]
            continue

        headcol = row.find("th", class_="headcol")
        if not headcol or not current_dates:
            continue

        pair_number = _parse_pair_number(headcol.select_one(".lesson"))
        starts_at = _text_or_none(headcol.select_one(".start"))
        ends_at = _text_or_none(headcol.select_one(".end"))

        for column_idx, cell in enumerate(row.find_all("td")):
            if column_idx >= len(current_dates):
                continue
            date_str = current_dates[column_idx]
            if not date_str:
                continue
            if not _within_range(date_str, date_from, date_to):
                continue

            for block in cell.select("div[data-toggle='popover']"):
                lesson = _build_lesson(
                    block,
                    date_str,
                    pair_number,
                    starts_at,
                    ends_at,
                    group_id,
                )
                if lesson:
                    lessons.append(lesson)

    lessons.sort(
        key=lambda item: (
            _date_key(item["date"]),
            item.get("pair_number") or 0,
            item.get("starts_at") or "",
            item.get("subject") or "",
        )
    )
    return lessons


def _build_lesson(
    node: Tag,
    date_str: str,
    pair_number: Optional[int],
    starts_at: Optional[str],
    ends_at: Optional[str],
    fallback_group: Optional[str],
) -> Optional[dict[str, Any]]:
    raw_parts = node.get("data-content", "").split("<br>")
    parts = [part.strip() for part in raw_parts if part and part.strip()]

    override = None
    if parts and _TIME_RANGE_RE.match(parts[0]):
        override = parts.pop(0)

    subject = None
    lesson_type = None
    room = None
    derived_group = None
    teacher = None
    notes: Optional[str] = None

    if parts:
        subject, lesson_type = _split_subject_and_type(parts[0])
    if len(parts) >= 2:
        room = parts[1]
    if len(parts) >= 3 and parts[2]:
        derived_group = parts[2]

    tail = parts[3:] if len(parts) > 3 else []
    note_parts: List[str] = []
    while tail and _looks_like_note(tail[-1]):
        note_parts.insert(0, tail.pop())
    if tail:
        teacher = ", ".join(tail)
    if note_parts:
        notes = " ".join(note_parts)

    text_parts = list(node.stripped_strings)
    if subject is None and text_parts:
        subject = text_parts[0]
    if lesson_type is None:
        lesson_type = _extract_type_from_text(text_parts)
    if room is None:
        room = _extract_room(text_parts)
    if teacher is None:
        teacher = _extract_teacher(text_parts)

    if override:
        match = _TIME_RANGE_RE.match(override)
        if match:
            starts_at = match.group(1)
            ends_at = match.group(2)

    if not subject and not teacher:
        return None

    lesson_group = (derived_group or fallback_group or None)

    payload = {
        "date": date_str,
        "pair_number": pair_number,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "subject": subject.strip() if subject else None,
        "type": lesson_type.strip() if lesson_type else None,
        "teacher": teacher.strip() if teacher else None,
        "room": room.strip() if room else None,
        "group_id": lesson_group.strip() if isinstance(lesson_group, str) else lesson_group,
        "notes": notes.strip() if notes else None,
    }
    payload["id"] = _hash_payload(payload)
    return payload


def _ensure_html(source: HtmlSource) -> str:
    if isinstance(source, (bytes, bytearray)):
        return source.decode("utf-8", errors="ignore")
    if isinstance(source, Path):
        return source.read_text(encoding="utf-8")
    if hasattr(source, "read"):
        return source.read()
    text = str(source)
    if "<" not in text and Path(text).exists():
        return Path(text).read_text(encoding="utf-8")
    return text


def _text_or_none(node: Optional[Tag]) -> Optional[str]:
    if node:
        text = node.get_text(strip=True)
        return text or None
    return None


def _parse_pair_number(node: Optional[Tag]) -> Optional[int]:
    if not node:
        return None
    match = _PAIR_RE.search(node.get_text(strip=True))
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def _within_range(date_str: str, start: Optional[Date], end: Optional[Date]) -> bool:
    if not start and not end:
        return True
    try:
        day = datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return True
    if start and day < start:
        return False
    if end and day > end:
        return False
    return True


def _date_key(date_str: str) -> Date:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return Date.max


def _split_subject_and_type(raw: str) -> Tuple[Optional[str], Optional[str]]:
    raw = raw.strip()
    if not raw:
        return None, None
    match = re.search(r"\[(.+?)\]\s*$", raw)
    if match:
        subject = raw[: match.start()].strip()
        lesson_type = match.group(1).strip()
    else:
        subject = raw
        lesson_type = None
    return subject or None, lesson_type or None


def _extract_type_from_text(parts: Sequence[str]) -> Optional[str]:
    for part in parts:
        if part.startswith("[") and part.endswith("]") and len(part) > 2:
            return part[1:-1]
    return None


def _extract_room(parts: Sequence[str]) -> Optional[str]:
    for part in parts:
        if _looks_like_room(part):
            return part
    return None


def _extract_teacher(parts: Sequence[str]) -> Optional[str]:
    for part in reversed(parts):
        if _looks_like_teacher(part):
            return part
    return None


def _looks_like_room(value: str) -> bool:
    lowered = value.lower()
    if any(token in lowered for token in ("ауд", "каб", "zoom", "онлайн", "кам.", "камера")):
        return True
    return bool(re.search(r"\d", value))


def _looks_like_teacher(value: str) -> bool:
    return bool(re.search(r"[А-ЯA-ZЁЙ][а-яa-zё]+\s+[А-ЯA-ZЁЙ]\.\s*[А-ЯA-ZЁЙ]\.", value))


def _looks_like_note(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(_NOTE_PREFIXES)


def _hash_payload(payload: dict[str, Any]) -> str:
    basis = {
        key: payload.get(key)
        for key in (
            "date",
            "pair_number",
            "starts_at",
            "ends_at",
            "subject",
            "type",
            "teacher",
            "room",
            "group_id",
            "notes",
        )
    }
    return hashlib.md5(
        json.dumps(basis, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


__all__ = ["parse_html_schedule"]
