from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
import uvloop
import asyncio
from app_api.di import AppProvider
from app_api.routes import events_router
import uvicorn
from app_api.config import settings, LOGGING_CONFIG
import logging
import logging.config

logger = logging.getLogger(__name__)

async def _main() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    container = make_async_container(AppProvider())
    app = FastAPI(
        title="Event Handler Service",
        version="0.1.0",
    )
    
    setup_dishka(container, app)
    
    app.include_router(events_router, prefix="/api/v1")
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    logger.info("Starting API server on port %s", settings.API_PORT)
    await uvicorn.Server(
        uvicorn.Config(
            app,
            host="0.0.0.0",  # noqa: S104
            port=settings.API_PORT,
            server_header=False,
            use_colors=False,
        )
    ).serve()


if __name__ == "__main__":
    asyncio.run(_main(), loop_factory=uvloop.Loop)