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
        assert response.user_id == request.user_id
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

        response = await stub.GetPost(posts_pb2.PostRef(id=post_response.id, user_id="tuser"))
        assert response.title == post_request.title
        assert response.description == post_request.description
        assert response.user_id == post_request.user_id
        assert response.tags == post_request.tags


@pytest.mark.asyncio
async def test_get_post_not_found():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        request = posts_pb2.PostRef(id=99999, user_id="tuser")
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
            await stub.GetPost(posts_pb2.PostRef(id=post_response.id, user_id="not_tuser"))
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
        assert response.user_id == post_request.user_id
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

        await stub.DeletePost(posts_pb2.PostRef(id=post_response.id, user_id="tuser"))

        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await stub.GetPost(posts_pb2.PostRef(id=post_response.id, user_id="tuser"))
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


@pytest.mark.asyncio
async def test_like_post_success():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        post_response = await stub.CreatePost(posts_pb2.CreatePostRequest(
            title="Test Post",
            user_id="tuser",
            description="This is a test post.",
            private=False,
            tags=["tag1", "tag2"]
        ))
        response = await stub.LikePost(posts_pb2.PostRef(id=post_response.id, user_id="tuser"))
        assert response is not None

@pytest.mark.asyncio
async def test_view_post_success():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        post_response = await stub.CreatePost(posts_pb2.CreatePostRequest(
            title="Test Post",
            user_id="tuser",
            description="This is a test post.",
            private=False,
            tags=["tag1", "tag2"]
        ))
        response = await stub.ViewPost(posts_pb2.PostRef(id=post_response.id, user_id="tuser"))
        assert response is not None

@pytest.mark.asyncio
async def test_create_comment_success():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        post_response = await stub.CreatePost(posts_pb2.CreatePostRequest(
            title="Test Post",
            user_id="tuser",
            description="This is a test post.",
            private=False,
            tags=["tag1", "tag2"]
        ))
        comment_text = "This is a test comment."
        create_comment_request = posts_pb2.CreateCommentRequest(
            post_id=post_response.id,
            user_id="tuser",
            text=comment_text
        )
        comment_response = await stub.CreateComment(create_comment_request)
        assert comment_response.text == comment_text
        assert comment_response.created_at is not None

@pytest.mark.asyncio
async def test_list_comments():
    async with grpc.aio.insecure_channel(POST_SERVER_ADDR) as channel:
        stub = posts_pb2_grpc.PostServiceStub(channel)
        post_response = await stub.CreatePost(posts_pb2.CreatePostRequest(
            title="Test Post",
            user_id="tuser",
            description="This is a test post.",
            private=False,
            tags=["tag1", "tag2"]
        ))
        for i in range(5):
            create_comment_request = posts_pb2.CreateCommentRequest(
                post_id=post_response.id,
                user_id="tuser",
                text=f"Comment {i}"
            )
            await stub.CreateComment(create_comment_request)
        list_comments_request = posts_pb2.ListCommentsRequest(
            post_id=post_response.id,
            page=1,
            limit=3,
            user_id="tuser"
        )
        list_comments_response = await stub.ListComments(list_comments_request)
        assert len(list_comments_response.com) == 3
        assert list_comments_response.total == 5
