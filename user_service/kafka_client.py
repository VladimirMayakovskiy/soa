import json
import asyncio
from aiokafka import AIOKafkaProducer
from config import settings

class AIOUserServiceProducer:
    def __init__(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def send_event(self, topic: str, event: dict) -> None:
        await self.start()
        try:
            await self._producer.send_and_wait(topic=topic, value=event)
        finally:
            await self.stop()

def get_producer() -> AIOUserServiceProducer:
    return AIOUserServiceProducer()