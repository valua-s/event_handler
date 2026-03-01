from __future__ import annotations

from typing import AsyncIterator
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
import logging
from redis.asyncio import Redis
from typing import AsyncGenerator, AsyncIterable
from notification_provider.config import settings
from notification_provider.services import DBService

logger = logging.getLogger(__name__)

class AppProvider(Provider):
    """Dishka provider for database dependencies."""

    @provide(scope=Scope.APP)
    async def provide_engine(self) -> AsyncIterable[AsyncEngine]:
        """Provide AsyncEngine as application-scoped singleton."""
        logger.info("Creating AsyncEngine with database URL")
        engine =  create_async_engine(
            settings.ASYNC_DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        yield engine
        await engine.dispose()
        

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
    def provide_db_service(self) -> DBService:
        """Provide DBService as application-scoped dependency."""
        logger.info("Initializing DBService")
        return DBService()

    
    @provide(scope=Scope.APP)
    async def get_redis(self) -> AsyncGenerator[Redis, None]:
        redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_USER,
            password=settings.REDIS_PASSWORD.get_secret_value(),
            decode_responses=True
        )
        try:
            yield redis
        finally:
            await redis.aclose()

