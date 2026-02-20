from typing import Any
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException, Query

from app_api.models import EventStatus
from app_api.schemas import (
    EventCreate,
    EventResponse,
    EventListResponse,
    EventUpdate,
)
from app_api.services import EventService


events_router = APIRouter(prefix="/events", tags=["events"])


@events_router.post("", response_model=EventResponse, status_code=201)
@inject
async def create_event(
    event_data: EventCreate,
    service: FromDishka[EventService],
):
    """Create a new event."""
    event = await service.create_event(event_data)
    return event
