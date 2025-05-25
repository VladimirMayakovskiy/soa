import asyncio
import logging

import grpc.aio

from proto import stats_pb2_grpc
from stats_service.service import StatService
from stats_service.kafka_client import AIOStatsServiceConsumer
from stats_service.config import settings

logging.basicConfig(level=logging.DEBUG)

async def serve():
    server = grpc.aio.server()
    stats_pb2_grpc.add_StatServiceServicer_to_server(StatService(), server)
    listen_addr = f"[::]:{settings.STATS_SERVER_PORT}"
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()

async def main():
    consumer = AIOStatsServiceConsumer()
    consumer_task = asyncio.create_task(consumer.start())
    server_task = asyncio.create_task(serve())
    await asyncio.gather(consumer_task, server_task)

if __name__ == "__main__":
    asyncio.run(main())