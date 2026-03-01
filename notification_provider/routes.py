from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from notification_provider.services import DBService
from notification_provider.helpers import check_headers_and_get_user_login
from redis.asyncio import Redis
import logging

logger = logging.getLogger()

notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])


async def event_stream(user_login: str, redis: Redis):
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"notifications:{user_login}")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                yield f"data: {data}\n\n"
    finally:
        await pubsub.unsubscribe(f"notifications:{user_login}")
        await pubsub.aclose()


@notifications_router.get("/sse")
@inject
async def get_sse_stream(
    request: Request,
    redis: FromDishka[Redis],
):
    user_login = await check_headers_and_get_user_login(request.headers)
    return StreamingResponse(
        event_stream(user_login, redis),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked",
        }
    )


@notifications_router.get("/unread_count")
@inject
async def get_unread_count(
    request: Request,
    session: FromDishka[AsyncSession],
    service: FromDishka[DBService]
):
    user_login = await check_headers_and_get_user_login(request.headers)
    unread_count = await service.get_unread_count_for_user(user_login, session)
    return {"unread_count": int(unread_count) if unread_count else 0}


@notifications_router.patch("/mark_as_read")
@inject
async def mark_as_read(
    notification_ids: list[UUID],
    request: Request,
    session: FromDishka[AsyncSession],
    service: FromDishka[DBService]
):
    user_login = await check_headers_and_get_user_login(request.headers)
    await service.mark_events_as_read(user_login,notification_ids, session)


@notifications_router.get("/unread")
@inject
async def get_unread_notifications( 
    request: Request,
    session: FromDishka[AsyncSession],
    service: FromDishka[DBService]
):
    user_login = await check_headers_and_get_user_login(request.headers)
    events = await service.get_unread_events_for_user(user_login, session)
    return events


@notifications_router.get("/all")
@inject
async def get_all_notifications(
    request: Request,
    session: FromDishka[AsyncSession],
    service: FromDishka[DBService]
):
    user_login = await check_headers_and_get_user_login(request.headers)
    events = await service.get_all_events_for_user(user_login, session)
    return events
    