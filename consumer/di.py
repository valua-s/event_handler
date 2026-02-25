from __future__ import annotations

from typing import AsyncIterator
import json
from dishka import Provider, Scope, provide
from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
import logging

from consumer.config import settings
from consumer.services import DBService

logger = logging.getLogger(__name__)

class AppProvider(Provider):
    """Dishka provider for database dependencies."""

    @provide(scope=Scope.APP)
    def provide_engine(self) -> AsyncEngine:
        """Provide AsyncEngine as application-scoped singleton."""
        logger.info("Creating AsyncEngine with database URL")
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
        logger.info("Creating AsyncSession factory")
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
        logger.debug("Creating new AsyncSession for request")
        async with factory() as session:
            yield session

    @provide(scope=Scope.APP)
    def provide_worker_service(self) -> DBService:
        """Provide DBService as application-scoped dependency."""
        logger.info("Initializing DBService")
        return DBService()

    @provide(scope=Scope.APP)
    async def kafka_consumer(self) -> AsyncIterator[AIOKafkaConsumer]:
        logger.info(f"Connecting to Kafka broker at {settings.KAFKA_URL}, topic: {settings.TOPIC_NAME}")
        consumer = AIOKafkaConsumer(
            settings.TOPIC_NAME,
            bootstrap_servers=settings.KAFKA_URL,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            enable_auto_commit=False,
            group_id="event_handler_group",
        )
        try:
            await consumer.start()
            logger.info("Kafka consumer started successfully")
            yield consumer
        finally:
            logger.info("Kafka consumer stopped")
            await consumer.stop()
