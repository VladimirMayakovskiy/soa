import pytest
import asyncio
import json
import time
from datetime import datetime
from aiokafka import AIOKafkaProducer

from stats_service.kafka_client import AIOStatsServiceConsumer


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.mark.asyncio
async def test_single_view_event(dummy_clickhouse):
    consumer = AIOStatsServiceConsumer()

    consume_task = asyncio.create_task(consumer.start())

    await asyncio.sleep(0.5)

    producer = AIOKafkaProducer(
        bootstrap_servers="kafka:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()
    try:
        payload = {
            "post_id": 777,
            "user_id": "integration_user",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        await producer.send_and_wait("views", payload)
    finally:
        await producer.stop()

    await asyncio.sleep(2)

    await consumer._consumer.stop()

    consume_task.cancel()
    try:
        await consume_task
    except asyncio.CancelledError:
        pass

    inserted = consumer._ch.inserted
    assert len(inserted) == 1

    event_date, post_id, user_id, metric = inserted[0]
    expected_date = datetime.fromisoformat(payload["timestamp"][:-1]).date()
    assert event_date == expected_date
    assert post_id == 777
    assert user_id == "integration_user"
    assert metric == "views"


@pytest.mark.asyncio
async def test_multiple_likes_and_comments(dummy_clickhouse):
    consumer = AIOStatsServiceConsumer()
    consume_task = asyncio.create_task(consumer.start())
    await asyncio.sleep(0.5)

    producer = AIOKafkaProducer(
        bootstrap_servers="kafka:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()
    try:
        base_iso = datetime.utcnow().isoformat() + "Z"
        msgs = [
            ("likes",    {"post_id": 300, "user_id": "A", "timestamp": base_iso}),
            ("likes",    {"post_id": 300, "user_id": "B", "timestamp": base_iso}),
            ("comments", {"post_id": 300, "user_id": "C", "timestamp": base_iso}),
        ]
        for topic, pl in msgs:
            await producer.send_and_wait(topic, pl)
    finally:
        await producer.stop()

    await asyncio.sleep(3)

    await consumer._consumer.stop()
    consume_task.cancel()
    try:
        await consume_task
    except asyncio.CancelledError:
        pass

    inserted = consumer._ch.inserted
    assert len(inserted) == 3

    expected_date = datetime.fromisoformat(base_iso[:-1]).date()
    assert inserted[0] == (expected_date, 300, "A", "likes")
    assert inserted[1] == (expected_date, 300, "B", "likes")
    assert inserted[2] == (expected_date, 300, "C", "comments")
