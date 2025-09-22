"""Client for fetching schedule data from cacs.spa.msu.ru."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

from .parse_html_schedule import parse_html_schedule

BASE_URL = "https://cacs.spa.msu.ru/time-table/group?type=0"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    " AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/124.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
    "X-Requested-With": "XMLHttpRequest",
}


@dataclass
class OptionItem:
    id: str
    name: str


class SpaScheduleClient:
    """Stateful helper that mimics the SPA timetable form workflow."""

    def __init__(self, base_url: str = BASE_URL) -> None:
        self.base_url = base_url
        self.session = requests.Session()
        self._csrf_token: Optional[str] = None
        self._hidden_inputs: Dict[str, str] = {}
        self._form_data: Dict[str, str] = {}
        self._last_soup: Optional[BeautifulSoup] = None

    # -- public API -----------------------------------------------------

    def list_faculties(self) -> List[OptionItem]:
        soup = self._ensure_initial_state()
        return self._extract_options(soup.select_one("#timetableform-facultyid"))

    def list_courses(self, faculty_id: str) -> List[OptionItem]:
        self._select_faculty(faculty_id)
        soup = self._submit_form()
        return self._extract_options(soup.select_one("#timetableform-course"))

    def list_groups(self, faculty_id: str, course: str) -> List[OptionItem]:
        self._select_faculty(faculty_id)
        self._select_course(course)
        soup = self._submit_form()
        return self._extract_options(soup.select_one("#timetableform-groupid"))

    def fetch_schedule(
        self,
        faculty_id: str,
        course: str,
        group_id: str,
        *,
        date_from: Optional[dt.date] = None,
        date_to: Optional[dt.date] = None,
    ) -> Dict[str, object]:
        self._select_faculty(faculty_id)
        self._select_course(course)
        if date_from:
            self._form_data["TimeTableForm[dateStart]"] = date_from.strftime("%d.%m.%Y")
        else:
            self._form_data.pop("TimeTableForm[dateStart]", None)
        if date_to:
            self._form_data["TimeTableForm[dateEnd]"] = date_to.strftime("%d.%m.%Y")
        else:
            self._form_data.pop("TimeTableForm[dateEnd]", None)
        self._select_group(group_id)
        soup = self._submit_form()
        html = str(soup)
        lessons = parse_html_schedule(
            html,
            group_id=self._current_group_name(soup),
            date_from=date_from,
            date_to=date_to,
        )
        return {
            "group": {
                "id": group_id,
                "name": self._current_group_name(soup),
            },
            "lessons": lessons,
        }

    # -- internal helpers ----------------------------------------------

    def _ensure_initial_state(self) -> BeautifulSoup:
        if self._last_soup is None:
            resp = self.session.get(self.base_url, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            self._update_state(soup)
        assert self._last_soup is not None
        return self._last_soup

    def _select_faculty(self, faculty_id: str) -> None:
        self._ensure_initial_state()
        self._form_data = {"TimeTableForm[facultyId]": str(faculty_id)}

    def _select_course(self, course: str) -> None:
        if "TimeTableForm[facultyId]" not in self._form_data:
            raise ValueError("Faculty must be selected before course")
        self._form_data["TimeTableForm[course]"] = str(course)
        self._form_data.pop("TimeTableForm[groupId]", None)

    def _select_group(self, group_id: str) -> None:
        if "TimeTableForm[course]" not in self._form_data:
            raise ValueError("Course must be selected before group")
        self._form_data["TimeTableForm[groupId]"] = str(group_id)

    def _submit_form(self) -> BeautifulSoup:
        soup = self._last_soup or self._ensure_initial_state()
        form = soup.select_one("#filter-form")
        if not form:
            raise RuntimeError("Form not found on timetable page")
        payload = dict(self._hidden_inputs)
        payload.update(self._form_data)
        payload.pop("_csrf-frontend", None)
        payload["_csrf-frontend"] = self._csrf_token or ""
        resp = self.session.post(self.base_url, data=payload, headers=_HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        self._update_state(soup)
        return soup

    def _update_state(self, soup: BeautifulSoup) -> None:
        token = soup.select_one("meta[name='csrf-token']")
        if not token or not token.get("content"):
            raise RuntimeError("CSRF token not found in response")
        self._csrf_token = token["content"]
        form = soup.select_one("#filter-form")
        hidden: Dict[str, str] = {}
        if form:
            for inp in form.find_all("input"):
                name = inp.get("name")
                if name:
                    hidden[name] = inp.get("value", "")
        self._hidden_inputs = hidden
        self._last_soup = soup

    @staticmethod
    def _extract_options(select: Optional[Tag]) -> List[OptionItem]:
        if select is None:
            return []
        items: List[OptionItem] = []
        for option in select.find_all("option"):
            value = option.get("value")
            if value is None or not value.strip():
                continue
            items.append(OptionItem(id=value.strip(), name=option.get_text(strip=True)))
        return items

    @staticmethod
    def _current_group_name(soup: BeautifulSoup) -> Optional[str]:
        opt = soup.select_one("#timetableform-groupid option[selected]")
        return opt.get_text(strip=True) if opt else None


__all__ = ["SpaScheduleClient", "OptionItem"]
