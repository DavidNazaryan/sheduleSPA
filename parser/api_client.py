"""REST API client for Android integration with CACS SPA MSU schedule parser."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

import requests

from .spa_client import SpaScheduleClient, OptionItem


@dataclass
class ApiResult:
    """Standard API response wrapper."""
    success: bool
    data: Any | None = None
    error: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }


class ScheduleApiClient:
    """High-level API client for Android app integration.
    
    This class provides a simple interface for fetching schedule data
    from cacs.spa.msu.ru and returning it in JSON-serializable format.
    
    Example usage:
        client = ScheduleApiClient()
        
        # Get all faculties
        faculties = client.get_faculties()
        
        # Get courses for faculty
        courses = client.get_courses(faculty_id="5")
        
        # Get groups for faculty and course
        groups = client.get_groups(faculty_id="5", course="1")
        
        # Get schedule for specific group
        schedule = client.get_schedule(
            faculty_id="5",
            course="1", 
            group_id="1317"
        )
    """

    def __init__(self, base_url: str = "https://cacs.spa.msu.ru/time-table/group?type=0"):
        self._client = SpaScheduleClient(base_url=base_url)

    def get_faculties(self) -> ApiResult:
        """Get list of all faculties (факультеты)."""
        try:
            items = self._client.list_faculties()
            return ApiResult(
                success=True,
                data=[{"id": item.id, "name": item.name} for item in items]
            )
        except Exception as e:
            return ApiResult(success=False, error=str(e))

    def get_courses(self, faculty_id: str) -> ApiResult:
        """Get list of courses (курсы) for a faculty."""
        try:
            items = self._client.list_courses(faculty_id)
            return ApiResult(
                success=True,
                data=[{"id": item.id, "name": item.name} for item in items]
            )
        except Exception as e:
            return ApiResult(success=False, error=str(e))

    def get_groups(self, faculty_id: str, course: str) -> ApiResult:
        """Get list of groups (группы) for a faculty and course."""
        try:
            items = self._client.list_groups(faculty_id, course)
            return ApiResult(
                success=True,
                data=[{"id": item.id, "name": item.name} for item in items]
            )
        except Exception as e:
            return ApiResult(success=False, error=str(e))

    def get_schedule(
        self,
        faculty_id: str,
        course: str,
        group_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> ApiResult:
        """Get schedule for a specific group.
        
        Args:
            faculty_id: Faculty ID from get_faculties()
            course: Course ID from get_courses()
            group_id: Group ID from get_groups()
            date_from: Optional start date in DD.MM.YYYY format
            date_to: Optional end date in DD.MM.YYYY format
            
        Returns:
            ApiResult with schedule data containing:
            - group: {"id": str, "name": str}
            - lessons: List of lesson dictionaries
        """
        try:
            from datetime import datetime
            
            df = None
            dt = None
            
            if date_from:
                df = datetime.strptime(date_from, "%d.%m.%Y").date()
            if date_to:
                dt = datetime.strptime(date_to, "%d.%m.%Y").date()
            
            result = self._client.fetch_schedule(
                faculty_id=faculty_id,
                course=course,
                group_id=group_id,
                date_from=df,
                date_to=dt,
            )
            return ApiResult(success=True, data=result)
        except ValueError as e:
            return ApiResult(success=False, error=f"Invalid date format: {e}")
        except Exception as e:
            return ApiResult(success=False, error=str(e))

    def search_group(self, query: str) -> ApiResult:
        """Search for groups by name substring.
        
        This is a convenience method that searches across all faculties
        and courses to find matching groups.
        
        Args:
            query: Substring to search for in group names (case-insensitive)
            
        Returns:
            ApiResult with list of matching groups including their path
        """
        try:
            matches = []
            query_lower = query.lower()
            
            faculties_result = self.get_faculties()
            if not faculties_result.success:
                return faculties_result
                
            for faculty in faculties_result.data:
                courses_result = self.get_courses(faculty["id"])
                if not courses_result.success:
                    continue
                    
                for course in courses_result.data:
                    groups_result = self.get_groups(faculty["id"], course["id"])
                    if not groups_result.success:
                        continue
                        
                    for group in groups_result.data:
                        if query_lower in group["name"].lower():
                            matches.append({
                                "id": group["id"],
                                "name": group["name"],
                                "faculty_id": faculty["id"],
                                "faculty_name": faculty["name"],
                                "course": course["id"],
                                "course_name": course["name"],
                            })
            
            return ApiResult(success=True, data=matches)
        except Exception as e:
            return ApiResult(success=False, error=str(e))


def to_json(result: ApiResult) -> str:
    """Convert ApiResult to JSON string."""
    return json.dumps(result.to_dict(), ensure_ascii=False)


__all__ = ["ScheduleApiClient", "ApiResult", "to_json"]
