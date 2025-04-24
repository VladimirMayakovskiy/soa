import os
import pytest
import grpc
from proto import posts_pb2, posts_pb2_grpc

POST_SERVER_ADDR = os.getenv("POST_SERVER_ADDR", "post_service:51075")


@pytest.mark.asyncio
async def test_create_post_success():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        request = posts_pb2.CreatePostRequest(
            title="Test Post",
            user_id="tuser",
            description="This is a test post.",
            private=False,
            tags=["tag1", "tag2"]
        )
        response = await stub.CreatePost(request)
        assert response.title == request.title
        assert response.description == request.description
        assert response.creator_id == request.user_id
        assert response.tags == request.tags


@pytest.mark.asyncio
async def test_get_post_success():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        post_request = posts_pb2.CreatePostRequest(
            title="Test Post",
            user_id="tuser",
            description="This is a test post.",
            private=False,
            tags=["tag1", "tag2"]
        )
        post_response = await stub.CreatePost(post_request)

        response = await stub.GetPost(posts_pb2.PostRequest(id=post_response.id, user_id="tuser"))
        assert response.title == post_request.title
        assert response.description == post_request.description
        assert response.creator_id == post_request.user_id
        assert response.tags == post_request.tags


@pytest.mark.asyncio
async def test_get_post_not_found():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        request = posts_pb2.PostRequest(id=99999, user_id="tuser")
        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.GetPost(request)
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

@pytest.mark.asyncio
async def test_get_post_private():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        post_request = posts_pb2.CreatePostRequest(
            title="Test Post",
            user_id="tuser",
            description="This is a test post.",
            private=True,
            tags=["tag1", "tag2"]
        )
        post_response = await stub.CreatePost(post_request)

        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.GetPost(posts_pb2.PostRequest(id=post_response.id, user_id="not_tuser"))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND


@pytest.mark.asyncio
async def test_update_post_success():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)

        post_request = posts_pb2.CreatePostRequest(
            title="Test Post",
            user_id="tuser",
            description="This is a test post.",
            private=False,
            tags=["tag1", "tag2"]
        )
        post_response = await stub.CreatePost(post_request)

        response = await stub.UpdatePost(
            posts_pb2.UpdatePostRequest(
                id=post_response.id,
                title="New Test Post Title",
                user_id="tuser",
                description="This is a test post.",
                private=False,
                tags=["tag1", "tag2", "tag_new"]
            )
        )

        assert response.title == "New Test Post Title"
        assert response.description == post_request.description
        assert response.creator_id == post_request.user_id
        assert "tag_new" in response.tags

@pytest.mark.asyncio
async def test_delete_post_success():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        post_request = posts_pb2.CreatePostRequest(
            title="Test Post",
            user_id="tuser",
            description="This is a test post.",
            private=False,
            tags=["tag1", "tag2"]
        )
        post_response = await stub.CreatePost(post_request)

        await stub.DeletePost(posts_pb2.PostRequest(id=post_response.id, user_id="tuser"))

        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.GetPost(posts_pb2.PostRequest(id=post_response.id, user_id="tuser"))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

@pytest.mark.asyncio
async def test_list_posts():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        for i in range(5):
            post_request = posts_pb2.CreatePostRequest(
                title=f"Test Post{i}",
                user_id="tuser",
                description="This is a test post.",
                private=False,
                tags=["tag1", "tag2"]
            )
            await stub.CreatePost(post_request)

        response = await stub.ListPosts(posts_pb2.ListPostsRequest(page=1, limit=3, user_id="tuser"))

        assert len(response.post) == 3

