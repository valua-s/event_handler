from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4
from typing import Optional, Any
from sqlalchemy import String, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventStatus(StrEnum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class EventType(StrEnum):
    IO = "io"
    CPU = "cpu"
    MIXED = "mixed"


class Event(Base):
    __tablename__ = "events"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    error_payload: Mapped[dict[str, Any]| None] = mapped_column(JSON, nullable=True)
    status: Mapped[EventStatus] = mapped_column(
        SQLEnum(EventStatus, native_enum=False),
        nullable=False,
        default=EventStatus.PENDING,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    number_consumers: Mapped[int] = mapped_column(nullable=True, default=0)
    tasks_types: Mapped[Optional[str]] = mapped_column(SQLEnum(EventType), nullable=True)
    