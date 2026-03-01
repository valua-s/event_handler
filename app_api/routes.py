from typing import Annotated
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Header
from fastapi.exceptions import HTTPException
from app_api.schemas import (
    EventCreate,
)
from app_api.services import EventService


events_router = APIRouter(prefix="/events", tags=["events"])


@events_router.post("", status_code=201)
@inject
async def create_event(
    event_data: EventCreate,
    service: FromDishka[EventService],
    service_name: Annotated[str, Header()],
):
    """Create a new event."""
    from_service = service_name
    if not from_service:
        raise HTTPException(
            status_code=400,
            detail="Missing 'Service' header indicating the source of the event"
        )
    await service.create_event(event_data, from_service)
