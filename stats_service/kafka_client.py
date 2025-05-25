import json
from aiokafka import AIOKafkaConsumer
import asyncio
from datetime import datetime
from stats_service.clickhouse_client import ClickHouseClient
from stats_service.config import settings
import logging

logging.basicConfig(level=logging.DEBUG)

TOPICS = ["views", "likes", "comments"]

class AIOStatsServiceConsumer:
    def __init__(self):
        print("BOOTSTRAP_SERVERS =", settings.KAFKA_BOOTSTRAP_SERVERS)
        self._consumer = AIOKafkaConsumer(
            *TOPICS,
            loop=asyncio.get_event_loop(),
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode("utf-8"))
        )
        self._ch = ClickHouseClient()

    async def start(self):
        await self._consumer.start()
        try:
            await self._consume()
        finally:
            await self._consumer.stop()

    async def _consume(self):
        async for msg in self._consumer:
            topic = msg.topic
            payload = msg.value
            ts = datetime.fromisoformat(payload.get("timestamp")[:-1])
            self._ch.insert_event(
                event_date=ts.date(),
                post_id=payload.get("post_id"),
                user_id=payload.get("user_id"),
                metric=topic
            )


