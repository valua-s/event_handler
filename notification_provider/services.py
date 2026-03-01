from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from consumer.models import Event, EventStatus
from consumer.schemas import EventResponse

logger = logging.getLogger(__name__)

MOSCOW_TIMEZONE = timezone(timedelta(hours=3))
class DBService:
    
    async def get_unread_events_for_user(self, user_login: str, session: AsyncSession) -> list[EventResponse]:
        """Get unread events for a specific user."""
        result = await session.scalars(
            select(Event).where(
                Event.to_user_login == user_login,
                Event.status == EventStatus.PROCESSED,
                Event.read_at.is_(None)
            ).order_by(Event.created_at.desc())
        )
        events = result.all()
        logger.info(f"Found {len(events)} unread events for user {user_login}")
        return [EventResponse.model_validate(event) for event in events]
    
    async def get_all_events_for_user(self, user_login: str, session: AsyncSession) -> list[EventResponse]:
        result = await session.scalars(
            select(Event).where(
                Event.to_user_login == user_login,
                ~Event.status.in_([EventStatus.FAILED]),
                Event.read_at.is_(None)
            ).order_by(Event.created_at.desc())
        )
        events = result.all()
        logger.info(f"Found {len(events)} all events for user {user_login}")
        return [EventResponse.model_validate(event) for event in events]
    
    async def mark_events_as_read(self, user_login: str, event_ids: list[UUID], session: AsyncSession) -> None:
        """Mark events as read."""
        logger.info(f"Marking events {event_ids} as read for user {user_login}")
        await session.execute(
            update(Event)
            .where(Event.id.in_(event_ids), Event.to_user_login == user_login)
            .values(
                read_at=datetime.now(MOSCOW_TIMEZONE),
                status=EventStatus.READ
            )
        )
        await session.commit()
    
    async def get_unread_count_for_user(self, user_login: str, session: AsyncSession) -> int:
        """Get count of unread events for a specific user."""
        result = await session.execute(
            select(func.count()).where(
                Event.to_user_login == user_login,
                Event.status == EventStatus.PROCESSED,
                Event.read_at.is_(None)
            )
        )
        return result.scalar_one()
