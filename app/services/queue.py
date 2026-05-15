import json
import uuid
from datetime import datetime
import aio_pika
from app.core.config import settings

class QueueService:
    def __init__(self):
        self.connection = None

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)

    async def publish_registration_event(self, user):
        await self.connect()
            
        async with self.connection.channel() as channel:

            exchange = await channel.declare_exchange(
                'app.events', 
                aio_pika.ExchangeType.DIRECT, 
                durable=True
            )
            
            message_body = {
                "eventId": str(uuid.uuid4()),
                "eventType": "user.registered",
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {
                    "userId": str(user.id),
                    "email": user.email,
                    "displayName": user.email.split('@')[0] 
                },
                "metadata": {"attempt": 1, "sourceService": "storage-api"}
            }

            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message_body).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key="user.registered"
            )