from datetime import datetime, timezone, timedelta
from aiokafka import AIOKafkaProducer
from app_api.config import settings


from app_api.schemas import EventCreate
from uuid import uuid4

MOSCOW_TIMEZONE = timezone(timedelta(hours=3))
class EventService:
    """Service for handling event business logic."""
    
    def __init__(self, kafka_producer: AIOKafkaProducer):
        self.kafka_producer = kafka_producer
    
    async def create_event(self, data: EventCreate, from_service: str) -> None:
        """Create a new event with PENDING status."""
        id_for_event = uuid4()
        await self.kafka_producer.send_and_wait(
            settings.TOPIC_NAME,
            {
                "id": str(id_for_event),
                "from_service": from_service,
                "to_user": data.to_user_login,
                "event_type": data.event_type,
                "payload": data.payload | {"created_at": datetime.now(MOSCOW_TIMEZONE).isoformat()},
            }
        )
    