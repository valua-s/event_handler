from dishka import make_async_container
import uvloop
import asyncio
import signal
from aiokafka import AIOKafkaConsumer
from consumer.di import AppProvider, DBService
from consumer.worker import ConsumerWorker
from consumer.config import setup_logging
import logging

logger = logging.getLogger(__name__)
    

async def _main() -> None:
    setup_logging()
    logger.info("Starting consumer application")
    loop = asyncio.get_event_loop()
    container = make_async_container(AppProvider())
    logger.info("Dependency container created")
    
    consumer: AIOKafkaConsumer = await container.get(AIOKafkaConsumer)
    db_service: DBService = await container.get(DBService)
    logger.info("Kafka consumer and database service initialized")
    
    task = loop.create_task(ConsumerWorker(consumer,db_service).start(container))
    logger.info("Consumer worker started")
    
    def handle_shutdown():
        logger.info("Shutdown signal received, cancelling consumer task")
        task.cancel()
    
    loop.add_signal_handler(signal.SIGTERM, handle_shutdown)
    loop.add_signal_handler(signal.SIGINT, handle_shutdown)
    
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Consumer task cancelled")
    finally:
        logger.info("Closing container and shutting down")    
        await container.close()


if __name__ == "__main__":
    asyncio.run(_main(), loop_factory=uvloop.Loop)