import grpc
from proto import posts_pb2, posts_pb2_grpc
from api_gateway.config import settings
from pydantic import BaseModel


class PostSchema(BaseModel):
    title: str
    description: str
    private: bool = False
    tags: list[str] = []


async def create_post(post_data: PostSchema, user_id: str):
    async with grpc.aio.insecure_channel(settings.POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        request = posts_pb2.CreatePostRequest(
            title=post_data.title,
            description=post_data.description,
            user_id=user_id,
            private=post_data.private,
            tags=post_data.tags
        )
        response = await stub.CreatePost(request)
        return response


async def update_post(post_id: int, post_data: PostSchema, user_id: str):
    async with grpc.aio.insecure_channel(settings.POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        request = posts_pb2.UpdatePostRequest(
            id=post_id,
            title=post_data.title,
            description=post_data.description,
            user_id=user_id,
            private=post_data.private,
            tags=post_data.tags
        )
        response = await stub.UpdatePost(request)
        return response


async def delete_post(post_id: int, user_id: str):
    async with grpc.aio.insecure_channel(settings.POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        request = posts_pb2.PostRequest(id=post_id, user_id=user_id)
        response = await stub.DeletePost(request)
        return response


async def get_post(post_id: int, user_id: str):
    async with grpc.aio.insecure_channel(settings.POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        request = posts_pb2.PostRequest(id=post_id, user_id=user_id)
        response = await stub.GetPost(request)
        return response


async def list_posts(page: int, limit: int, user_id: str):
    async with grpc.aio.insecure_channel(settings.POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        request = posts_pb2.ListPostsRequest(page=page, limit=limit, user_id=user_id)
        response = await stub.ListPosts(request)
        return response
