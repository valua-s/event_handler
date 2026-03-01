from aiokafka import AIOKafkaConsumer
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from consumer.services import DBService
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)

class ConsumerWorker:
    def __init__(self, consumer: AIOKafkaConsumer, service: DBService):
        self.consumer: AIOKafkaConsumer = consumer
        self.service: DBService = service
    
    async def start(self, container: AsyncContainer):
        try:
            async for msg in self.consumer:
                event_data = msg.value
                event_id = event_data.get("id")
                if not event_id:
                    continue
                asyncio.create_task(self.process_message(msg, event_data, container)) 
        finally:
            await self.consumer.stop()
    
    async def process_message(self, msg, event_data, container: AsyncContainer):
        async with container() as request_container:
            session = await request_container.get(AsyncSession)
            redis = await request_container.get(Redis)
            
            event_id = event_data.get("id")
            try:
                is_need_to_publish = await self.service.is_need_to_publish(event_data, session)
                if is_need_to_publish:
                    try:
                        result = await redis.publish(f"notifications:{event_data.get('to_user')}", "New event")
                        logger.info("Published to redis, receivers: %s", result)
                    except Exception as e:
                        logger.exception(f"Failed to publish notification for event {event_id}: {e}")
                        await self.service.mark_as_fail(event_id, session)
                    else:
                        await self.service.mark_as_processed(event_id, session)
                    await self.consumer.commit()
            except Exception as e:
                logger.exception("Error while working with event %s", e)
