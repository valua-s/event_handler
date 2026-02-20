from datetime import datetime, timezone
from typing import Any
from uuid import UUID
from aiokafka import AIOKafkaProducer
from app_api.config import settings

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app_api.models import Event, EventStatus
from app_api.schemas import EventCreate, EventUpdate


class EventService:
    """Service for handling event business logic."""
    
    def __init__(self, session: AsyncSession, kafka_producer: AIOKafkaProducer):
        self.session = session
        self.kafka_producer = kafka_producer
    
    async def create_event(self, data: EventCreate) -> Event:
        """Create a new event with PENDING status."""
        event = Event(
            event_type=data.event_type,
            payload=data.payload,
            status=EventStatus.PENDING,
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        await self.kafka_producer.send_and_wait(
            settings.TOPIC_NAME,
            {
                "id": str(event.id),
                "event_type": event.event_type,
            }
        )
        return event
    
    async def get_event(self, event_id: UUID) -> Event | None:
        """Get event by ID."""
        result = await self.session.execute(
            select(Event).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()
    
    async def list_events(
        self,
        offset: int = 0,
        limit: int = 100,
        status: EventStatus | None = None,
        event_type: str | None = None,
    ) -> tuple[list[Event], int]:
        """List events with optional filtering and pagination."""
        query = select(Event)
        
        if status:
            query = query.where(Event.status == status)
        if event_type:
            query = query.where(Event.event_type == event_type)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()
        
        # Get paginated results
        query = query.offset(offset).limit(limit).order_by(Event.created_at.desc())
        result = await self.session.execute(query)
        events = list(result.scalars().all())
        
        return events, total
    
    async def update_event_status(
        self,
        event_id: UUID,
        data: EventUpdate,
    ) -> Event | None:
        """Update event status and optionally payload."""
        event = await self.get_event(event_id)
        if not event:
            return None
        
        event.status = data.status
        
        # Update processed_at when status changes to PROCESSED or FAILED
        if data.status in (EventStatus.PROCESSED, EventStatus.FAILED):
            event.processed_at = datetime.now(timezone.utc)
        
        # Update payload if provided
        if data.payload is not None:
            event.payload = data.payload
        
        await self.session.commit()
        await self.session.refresh(event)
        return event
    
    async def mark_as_processed(self, event_id: UUID) -> Event | None:
        """Mark event as processed."""
        return await self.update_event_status(
            event_id,
            EventUpdate(status=EventStatus.PROCESSED)
        )
    
    async def mark_as_failed(
        self,
        event_id: UUID,
        error_payload: dict[str, Any] | None = None
    ) -> Event | None:
        """Mark event as failed with optional error details."""
        payload = error_payload if error_payload else {}
        return await self.update_event_status(
            event_id,
            EventUpdate(status=EventStatus.FAILED, payload=payload)
        )
    
    async def get_pending_events(self, limit: int = 100) -> list[Event]:
        """Get pending events for processing."""
        result = await self.session.execute(
            select(Event)
            .where(Event.status == EventStatus.PENDING)
            .order_by(Event.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())