from datetime import datetime
from uuid import UUID
from typing import Any

from pydantic import BaseModel, ConfigDict

from consumer.models import EventStatus


class EventCreate(BaseModel):
    """DTO for creating a new event."""
    
    id: UUID
    event_type: str
    from_service: str
    payload: dict[str, Any]
    to_user_login: str

class EventUpdate(BaseModel):
    """DTO for updating event status."""
    
    status: EventStatus
    payload: dict[str, Any] | None = None
    error_payload: dict[str, Any] | None = None


class EventResponse(BaseModel):
    """DTO for returning event data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    event_type: str
    payload: dict[str, Any]
    status: EventStatus
    created_at: datetime
    processed_at: datetime | None = None


class EventListResponse(BaseModel):
    """DTO for paginated event list."""
    
    items: list[EventResponse]
    total: int
    offset: int
    limit: int