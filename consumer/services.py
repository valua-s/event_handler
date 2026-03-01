from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from consumer.models import Event, EventStatus
from consumer.schemas import EventCreate

logger = logging.getLogger(__name__)

MOSCOW_TIMEZONE = timezone(timedelta(hours=3))
class DBService:
    
    async def get_event(self, event_id: UUID, session: AsyncSession) -> Event | None:
        """Get event by ID."""
        logger.debug(f"Fetching event {event_id} from database")
        result = await session.execute(
            select(Event).where(Event.id == event_id)
        )
        event = result.scalar_one_or_none()
        if event:
            logger.debug(f"Event {event_id} found with status: {event.status}")
        else:
            logger.warning(f"Event {event_id} not found in database")
        return event
    
    async def update_event_status(
        self,
        event_id: UUID,
        status: EventStatus,
        session: AsyncSession
    ) -> Event | None:
        """Update event status and optionally payload."""
        logger.info(f"Updating event {event_id} status to {status}")
        event = await self.get_event(event_id, session)
        if not event:
            logger.error(f"Cannot update event {event_id}: event not found")
            return None
        if event.status == EventStatus.PROCESSED:
            logger.warning(f"Event {event_id} is already processed. Skipping update.")
            return None
        event.status = status
        await session.commit()
        logger.info(f"Event {event_id} successfully updated with status {status}")
    
    async def mark_as_fail(self, event_id: UUID, session: AsyncSession) -> None:
        """Mark event as failed."""
        logger.info(f"Marking event {event_id} as failed")
        await self.update_event_status(
            event_id,
            status=EventStatus.FAILED,
            session=session
        )
    
    async def mark_as_processed(self, event_id: UUID, session: AsyncSession) -> None:
        logger.info(f"Marking event {event_id} as processed")
        await self.update_event_status(
            event_id,
            status=EventStatus.PROCESSED,
            session=session
        )
        
    async def is_need_to_publish(self, raw_data: dict[str, Any], session: AsyncSession) -> bool:
        """Check if event is already processed."""
        event_id = raw_data.get("id")
        if not event_id:
            logger.error("Event data missing 'id' field")
            raise ValueError("Event data must include 'id'")
        logger.debug(f"Checking if event {event_id} is already processed")
        event = await self.get_event(event_id, session)
        if not event:
            await self.create_event(raw_data, session)
            return True
        if event.status == EventStatus.FAILED:
            return True
        return False

    
    async def create_event(self, raw_data: dict[str, Any], session: AsyncSession) -> Event:
        """Create a new event with PROCESSED status."""
        try:
            data = EventCreate.model_validate(raw_data)
        except Exception as e:
            logger.error("Invalid event data: %s", e)
            raise ValueError
        logger.info(f"Creating new event of type {data.event_type}")
        value = data.payload.get("created_at", datetime.now(MOSCOW_TIMEZONE))
        event = Event(
            created_at=datetime.fromisoformat(value) if isinstance(value, str) else value,
            **data.model_dump()
        )
        session.add(event)
        try:
            await session.commit()
            await session.refresh(event)
            logger.info(f"Event {event.id} created with status PROCESSED")
        except Exception as e:
            logger.exception(e)
            raise
        return event
