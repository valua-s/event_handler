from typing import Any

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """DTO for creating a new event."""
    
    event_type: str = Field(..., min_length=1, max_length=255)
    payload: dict[str, Any] = Field(...)
    to_user_login: str = Field(..., min_length=3, max_length=255)
