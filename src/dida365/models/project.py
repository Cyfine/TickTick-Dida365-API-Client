"""Project-related models for the API client."""
from enum import Enum
from typing import List, Optional

from pydantic import Field, field_validator

from .base import BaseApiModel, SortableMixin, TimestampMixin
from .task import Task


class ViewMode(str, Enum):
    """Project view mode options.
    
    As specified in the API documentation:
    - list: Default list view
    - kanban: Kanban board view
    - timeline: Timeline/calendar view
    """

    LIST = "list"
    KANBAN = "kanban"
    TIMELINE = "timeline"

    @classmethod
    def _missing_(cls, value: str) -> Optional["ViewMode"]:
        """Handle case-insensitive lookup with warning."""
        if not isinstance(value, str):
            return None
            
        for member in cls:
            if member.value.lower() == value.lower():
                if member.value != value:
                    import warnings
                    warnings.warn(
                        f"ViewMode value '{value}' was converted to '{member.value}'. "
                        "Please use exact case for better compatibility.",
                        UserWarning
                    )
                return member
        return None


class ProjectKind(str, Enum):
    """Project kind options.
    
    As specified in the API documentation:
    - TASK: Regular task project
    - NOTE: Note-taking project
    """

    TASK = "TASK"
    NOTE = "NOTE"

    @classmethod
    def _missing_(cls, value: str) -> Optional["ProjectKind"]:
        """Handle case-insensitive lookup with warning."""
        if not isinstance(value, str):
            return None
            
        for member in cls:
            if member.value.upper() == value.upper():
                if member.value != value:
                    import warnings
                    warnings.warn(
                        f"ProjectKind value '{value}' was converted to '{member.value}'. "
                        "Please use exact case for better compatibility.",
                        UserWarning
                    )
                return member
        return None


class ProjectPermission(str, Enum):
    """Project permission levels.
    
    As specified in the API documentation:
    - read: Read-only access
    - write: Full read/write access
    - comment: Can read and comment only
    """

    READ = "read"
    WRITE = "write"
    COMMENT = "comment"


class ProjectBase(BaseApiModel, SortableMixin):
    """Base model for project data."""

    name: Optional[str] = Field(None, description="Project name")
    color: Optional[str] = Field(None, description="Project color (hex code)")
    view_mode: Optional[ViewMode] = Field(
        default=ViewMode.LIST,
        description="View mode (list, kanban, timeline)"
    )
    kind: Optional[ProjectKind] = Field(
        default=ProjectKind.TASK,
        description="Project kind (TASK, NOTE)"
    )

    @field_validator("color")
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize color hex code format."""
        if v is None:
            return v
            
        # Remove any whitespace
        v = v.strip()
        
        # Handle the # prefix
        if not v.startswith("#"):
            v = f"#{v}"
        
        # Basic hex color validation
        if not (len(v) == 7 and all(c in "0123456789ABCDEFabcdef#" for c in v)):
            raise ValueError(
                f"Invalid color hex code '{v}'. "
                "Must be a 6-digit hex code with optional '#' prefix (e.g., '#FF0000' or 'FF0000')"
            )
        
        return v


class ProjectCreate(BaseApiModel):
    """Model for creating a new project.
    
    Example:
        ```python
        project = ProjectCreate(
            name="My Project",
            color="#FF0000",
            view_mode=ViewMode.KANBAN,
            kind=ProjectKind.TASK
        )
        ```
    """
    name: str = Field(..., description="Project name")
    color: Optional[str] = Field(None, description="Project color (hex code)")
    view_mode: ViewMode = Field(
        default=ViewMode.LIST,
        description="View mode (list, kanban, timeline)"
    )
    kind: ProjectKind = Field(
        default=ProjectKind.TASK,
        description="Project kind (TASK, NOTE)"
    )

    @field_validator("color")
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize color hex code format."""
        if v is None:
            return v
            
        # Remove any whitespace
        v = v.strip()
        
        # Handle the # prefix
        if not v.startswith("#"):
            v = f"#{v}"
        
        # Basic hex color validation
        if not (len(v) == 7 and all(c in "0123456789ABCDEFabcdef#" for c in v)):
            raise ValueError(
                f"Invalid color hex code '{v}'. "
                "Must be a 6-digit hex code with optional '#' prefix (e.g., '#FF0000' or 'FF0000')"
            )
        
        return v


class ProjectUpdate(ProjectBase):
    """Model for updating an existing project.
    
    Example:
        ```python
        update = ProjectUpdate(
            id="project_id",
            name="Updated Name",
            view_mode=ViewMode.TIMELINE
        )
        ```
    """

    id: str = Field(..., description="Project identifier")


class Project(ProjectBase, TimestampMixin):
    """Model for a complete project.
    
    Includes all project data including system fields like ID and timestamps.
    """

    id: str = Field(..., description="Project identifier")
    closed: bool = Field(default=False, description="Whether the project is closed")
    group_id: Optional[str] = Field(None, description="Project group identifier")
    permission: ProjectPermission = Field(
        default=ProjectPermission.WRITE,
        description="Access permission level"
    )


class Column(BaseApiModel, SortableMixin):
    """Model for a project column."""

    id: str = Field(..., description="Column identifier")
    project_id: str = Field(..., description="Project identifier")
    name: str = Field(..., description="Column name")


class ProjectData(BaseApiModel):
    """Model for complete project data including tasks and columns."""

    project: Project = Field(..., description="Project information")
    tasks: List[Task] = Field(default_factory=list, description="List of tasks in the project")
    columns: List[Column] = Field(default_factory=list, description="List of columns in the project") 