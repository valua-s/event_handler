from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
import uvloop
import asyncio
from notification_provider.di import AppProvider
from notification_provider.routes import notifications_router
import uvicorn
from notification_provider.config import settings, LOGGING_CONFIG
import logging
import logging.config
from fastapi.openapi.utils import get_openapi

logger = logging.getLogger(__name__)


async def _main() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    container = make_async_container(AppProvider())
    app = FastAPI(
        title="Notification Service",
        version="0.1.0",
        swagger_ui_parameters={"persistAuthorization": True},
    )
    setup_dishka(container, app)
    
    app.include_router(notifications_router, prefix="/api/v1")
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )
        schema["components"]["securitySchemes"] = {
            "X-User-Id": {
                "type": "apiKey",
                "in": "header",
                "name": "X-User-Id",
            }
        }
        schema["security"] = [{"X-User-Id": []}]
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi   # type: ignore
    
    logger.info("Starting API server on port %s", settings.NOTIFICATION_API_PORT)
    await uvicorn.Server(
        uvicorn.Config(
            app,
            host="0.0.0.0",  # noqa: S104
            port=settings.NOTIFICATION_API_PORT,
            server_header=False,
            use_colors=False,
        )
    ).serve()


if __name__ == "__main__":
    asyncio.run(_main(), loop_factory=uvloop.Loop)