"""Base models for the API client."""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseApiModel(BaseModel):
    """Base model for all API models."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda s: ''.join(word.capitalize() if i else word
                                        for i, word in enumerate(s.split('_'))),
    )


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""

    created_time: Optional[datetime] = Field(None, description="Creation timestamp")
    modified_time: Optional[datetime] = Field(None, description="Last modification timestamp")


class SortableMixin(BaseModel):
    """Mixin for models with sort order."""

    sort_order: Optional[int] = Field(None, description="Sort order value") 