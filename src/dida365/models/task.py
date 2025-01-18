"""Task-related models for the API client."""
from datetime import datetime, timezone
from enum import IntEnum
from typing import List, Optional, Dict, Any

from pydantic import Field, field_serializer

from .base import BaseApiModel, SortableMixin, TimestampMixin


class TaskPriority(IntEnum):
    """Task priority levels."""

    NONE = 0
    LOW = 1
    MEDIUM = 3
    HIGH = 5


class TaskStatus(IntEnum):
    """Task status values."""

    NORMAL = 0
    COMPLETED = 2


class ChecklistItemStatus(IntEnum):
    """Checklist item status values."""

    NORMAL = 0
    COMPLETED = 1


class ChecklistItem(BaseApiModel, SortableMixin):
    """Model for a checklist item (subtask)."""

    id: Optional[str] = Field(None, description="Checklist item identifier")
    title: str = Field(..., description="Checklist item title")
    status: ChecklistItemStatus = Field(
        default=ChecklistItemStatus.NORMAL,
        description="Completion status"
    )
    completed_time: Optional[datetime] = Field(None, description="Completion timestamp")
    is_all_day: bool = Field(default=False, description="Whether the item is all-day")
    start_date: Optional[datetime] = Field(None, description="Start date and time")
    time_zone: Optional[str] = Field(None, description="Time zone")


class TaskBase(BaseApiModel, SortableMixin):
    """Base model for task data."""

    title: str = Field(..., description="Task title")
    content: Optional[str] = Field(None, description="Task content")
    desc: Optional[str] = Field(None, description="Task description")
    is_all_day: bool = Field(default=False, description="Whether the task is all-day")
    start_date: Optional[datetime] = Field(None, description="Start date and time")
    due_date: Optional[datetime] = Field(None, description="Due date and time")
    time_zone: Optional[str] = Field(None, description="Time zone")
    reminders: List[str] = Field(default_factory=list, description="List of reminder triggers")
    repeat_flag: Optional[str] = Field(None, description="Recurring rules")
    priority: TaskPriority = Field(default=TaskPriority.NONE, description="Task priority")
    items: List[ChecklistItem] = Field(default_factory=list, description="List of checklist items")

    @field_serializer('start_date', 'due_date')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        if dt is None:
            return None
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000")

    @field_serializer('priority')
    def serialize_priority(self, priority: TaskPriority, _info) -> int:
        return int(priority)


class TaskCreate(TaskBase):
    """Model for creating a new task."""

    project_id: str = Field(..., description="Project identifier")


class TaskUpdate(TaskBase):
    """Model for updating an existing task."""

    id: str = Field(..., description="Task identifier")
    project_id: str = Field(..., description="Project identifier")


class Task(TaskBase, TimestampMixin):
    """Model for a complete task."""

    id: str = Field(..., description="Task identifier")
    project_id: str = Field(..., description="Project identifier")
    status: TaskStatus = Field(
        default=TaskStatus.NORMAL,
        description="Task status"
    )
    completed_time: Optional[datetime] = Field(None, description="Completion timestamp") 