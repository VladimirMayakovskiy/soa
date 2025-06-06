import grpc
from proto import posts_pb2, posts_pb2_grpc
from api_gateway.config import settings
from pydantic import BaseModel


def _channel():
    return grpc.aio.insecure_channel(settings.POST_SERVER_ADDR)

class PostSchema(BaseModel):
    title: str
    description: str
    private: bool = False
    tags: list[str] = []


async def create_post(post_data: PostSchema, user_id: str):
    async with _channel() as ch:
        stub = posts_pb2_grpc.PostServiceStub(ch)
        req = posts_pb2.CreatePostRequest(
            title=post_data.title,
            description=post_data.description,
            user_id=user_id,
            private=post_data.private,
            tags=post_data.tags
        )
        return await stub.CreatePost(req)


async def update_post(post_id: int, post_data: PostSchema, user_id: str):
    async with _channel() as ch:
        stub = posts_pb2_grpc.PostServiceStub(ch)
        req = posts_pb2.UpdatePostRequest(
            id=post_id,
            title=post_data.title,
            description=post_data.description,
            user_id=user_id,
            private=post_data.private,
            tags=post_data.tags
        )
        return await stub.UpdatePost(req)


async def delete_post(post_id: int, user_id: str):
    async with _channel() as ch:
        stub = posts_pb2_grpc.PostServiceStub(ch)
        req = posts_pb2.PostRequest(id=post_id, user_id=user_id)
        return await stub.DeletePost(req)


async def get_post(post_id: int, user_id: str):
    async with _channel() as ch:
        stub = posts_pb2_grpc.PostServiceStub(ch)
        req = posts_pb2.PostRequest(id=post_id, user_id=user_id)
        return await stub.GetPost(req)


async def list_posts(page: int, limit: int, user_id: str):
    async with _channel() as ch:
        stub = posts_pb2_grpc.PostServiceStub(ch)
        req = posts_pb2.ListPostsRequest(page=page, limit=limit, user_id=user_id)
        return await stub.ListPosts(req)


async def view(post_id: int, user_id: str):
    async with _channel() as ch:
        stub = posts_pb2_grpc.PostServiceStub(ch)
        req = posts_pb2.PostRef(id=post_id, user_id=user_id)
        return await stub.ViewPost(req)


async def like(post_id: int, user_id: str):
    async with _channel() as ch:
        stub = posts_pb2_grpc.PostServiceStub(ch)
        req = posts_pb2.PostRef(id=post_id, user_id=user_id)
        return await stub.LikePost(req)


async def create_comment(post_id: int, user_id: str, text: str):
    async with _channel() as ch:
        stub = posts_pb2_grpc.PostServiceStub(ch)
        req = posts_pb2.CreateCommentRequest(post_id=post_id, text=text, user_id=user_id)
        return await stub.CreateComment(req)

async def list_comments(post_id: int, user_id: str, page: int, limit: int):
    async with _channel() as ch:
        stub = posts_pb2_grpc.PostServiceStub(ch)
        req = posts_pb2.ListCommentsRequest(post_id=post_id, user_id=user_id, page=page, limit=limit)
        return await stub.ListComments(req)