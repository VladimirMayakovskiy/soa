import asyncio
import grpc
from post_service.service import PostService
from proto import posts_pb2_grpc
from post_service.config import settings
import logging

logging.basicConfig(level=logging.DEBUG)

async def serve():
    server = grpc.aio.server()
    posts_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    listen_addr = f"[::]:{settings.POST_SERVER_PORT}" #51075
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())