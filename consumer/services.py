from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from consumer.models import Event, EventStatus, EventType
from consumer.schemas import EventUpdate

logger = logging.getLogger(__name__)


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
        data: EventUpdate,
        session: AsyncSession
    ) -> Event | None:
        """Update event status and optionally payload."""
        logger.info(f"Updating event {event_id} status to {data.status}")
        event = await self.get_event(event_id, session)
        if not event:
            logger.error(f"Cannot update event {event_id}: event not found")
            return None
        
        event.status = data.status
        event.number_consumers = 1
        event.tasks_types = EventType.MIXED
        
        # Update processed_at when status changes to PROCESSED or FAILED
        if data.status in (EventStatus.PROCESSED, EventStatus.FAILED):
            event.processed_at = datetime.now(timezone.utc)
        
        # Update payload if provided
        if data.payload is not None:
            logger.debug(f"Updating event {event_id} payload")
            event.payload = data.payload
        
        if data.error_payload is not None:
            logger.debug(f"Updating event {event_id} error payload")
            event.error_payload = data.error_payload
        
        await session.commit()
        logger.info(f"Event {event_id} successfully updated with status {data.status}")
    
    async def mark_as_processed(self, event_id: UUID, session: AsyncSession) -> None:
        """Mark event as processed."""
        logger.info(f"Marking event {event_id} as processed")
        await self.update_event_status(
            event_id,
            EventUpdate(status=EventStatus.PROCESSED),
            session=session
        )
        
    async def check_is_processed(self, event_id: UUID, session: AsyncSession) -> bool:
        """Check if event is already processed."""
        logger.debug(f"Checking if event {event_id} is already processed")
        event = await self.get_event(event_id, session)
        if event:
            is_processed = event.status == EventStatus.PROCESSED
            logger.debug(f"Event {event_id} processed status: {is_processed}")
            return is_processed
        logger.warning(f"Event {event_id} not found when checking processed status")
        return False
    
    async def mark_as_failed(
        self,
        event_id: UUID,
        session: AsyncSession,
        error_payload: dict[str, Any] | None = None
    ) -> None:
        """Mark event as failed with optional error details."""
        logger.warning(f"Marking event {event_id} as failed")
        await self.update_event_status(
            event_id,
            EventUpdate(status=EventStatus.FAILED, error_payload=error_payload if error_payload else {}),
            session=session
        )
