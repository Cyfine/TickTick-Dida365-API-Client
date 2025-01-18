"""Dida365/TickTick API client package."""

from .client import Dida365Client
from .config import ApiConfig, ServiceType
from .exceptions import (
    ApiError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError
)
from .models.project import (
    Column,
    Project,
    ProjectCreate,
    ProjectData,
    ProjectKind,
    ProjectPermission,
    ProjectUpdate,
    ViewMode,
)
from .models.task import (
    ChecklistItem,
    Task,
    TaskCreate,
    TaskPriority,
    TaskStatus,
    TaskUpdate,
)

__version__ = "0.1.0"
__all__ = [
    # Main client
    "Dida365Client",
    # Configuration
    "ApiConfig",
    "ServiceType",
    # Exceptions
    "ApiError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    # Project models
    "Column",
    "Project",
    "ProjectCreate",
    "ProjectData",
    "ProjectKind",
    "ProjectPermission",
    "ProjectUpdate",
    "ViewMode",
    # Task models
    "ChecklistItem",
    "Task",
    "TaskCreate",
    "TaskPriority",
    "TaskStatus",
    "TaskUpdate",
] 