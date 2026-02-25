from aiokafka import AIOKafkaConsumer
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from consumer.services import DBService
import logging
import random

logger = logging.getLogger(__name__)

class ConsumerWorker:
    def __init__(self, consumer: AIOKafkaConsumer, service: DBService):
        self.consumer = consumer
        self.service = service
    
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
            event_id = event_data.get("id")
            try:
                if event_data.get("event_type", None):
                    is_processed = await self.service.check_is_processed(event_id, session)
                    if is_processed:
                        await self.consumer.commit()
                        return
                    event_type = event_data.get("event_type")
                    if "io" not in event_type and "cpu" not in event_type:
                        event_type = random.choice(["io", "cpu"])
                    if ("io" in str(event_type)):
                        await asyncio.sleep(1)
                        
                    elif ("cpu" in str(event_data.get("event_type"))):
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, lambda: sum(i * i for i in range(10**6)))
                        logger.info(f"Calculation result: {result}")
                    await self.service.mark_as_processed(event_id, session)
                    await self.consumer.commit()
            except Exception as e:
                await self.service.mark_as_failed(event_id, session, error_payload={"error": str(e)})
