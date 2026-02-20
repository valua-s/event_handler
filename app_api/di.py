from __future__ import annotations

from typing import AsyncIterator
import json
from dishka import Provider, Scope, provide
from aiokafka import AIOKafkaProducer
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app_api.config import settings
from app_api.services import EventService


class AppProvider(Provider):
    """Dishka provider for database dependencies."""

    @provide(scope=Scope.APP)
    def provide_engine(self) -> AsyncEngine:
        """Provide AsyncEngine as application-scoped singleton."""
        return create_async_engine(
            settings.ASYNC_DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )

    @provide(scope=Scope.APP)
    def provide_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        """Provide session factory as application-scoped singleton."""
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        """Provide AsyncSession as request-scoped dependency."""
        async with factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def provide_event_service(self, session: AsyncSession, kafka_producer: AIOKafkaProducer) -> EventService:
        """Provide EventService as request-scoped dependency."""
        return EventService(session, kafka_producer)

    @provide(scope=Scope.APP)
    async def kafka_producer(self) -> AsyncIterator[AIOKafkaProducer]:
        producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_URL, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        try:
            await producer.start()
            yield producer
        finally:
            await producer.stop()
