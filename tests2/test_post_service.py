import pytest
import asyncio
import grpc
from google.protobuf.empty_pb2 import Empty

from post_service.models import Post, Comment
from post_service.utils import create_post as create_post_util, create_comment as create_comment_util
from proto import posts_pb2
from sqlalchemy.orm import Session


class FakeContext:
    def __init__(self):
        self._aborted = False
        self._code = None
        self._details = None

    async def abort(self, code, details: str):
        self._aborted = True
        self._code = code
        self._details = details
        raise grpc.RpcError(f"{code.name}: {details}")


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_create_post_and_persist(db_session_post, post_service):
    req = posts_pb2.CreatePostRequest(
        title="Тест-заголовок",
        description="Описание тест-поста",
        user_id="user42",
        private=False,
        tags=["t1", "t2"]
    )
    returned= run_async(post_service.CreatePost(req, None))

    assert returned.id == 1
    assert returned.title == "Тест-заголовок"
    assert returned.description == "Описание тест-поста"
    assert returned.user_id == "user42"
    assert returned.private is False
    assert list(returned.tags) == ["t1", "t2"]
    assert returned.created_at

    db_session_post.expire_all()
    post_in_db = db_session_post.query(Post).filter(Post.id == returned.id).first()
    assert post_in_db is not None
    assert post_in_db.title == "Тест-заголовок"
    assert post_in_db.user_id == "user42"
    assert post_in_db.tags == "t1,t2"


def test_get_post_not_found(db_session_post: Session, post_service):
    ctx = FakeContext()
    req = posts_pb2.PostRef(id=999, user_id="anyone")

    with pytest.raises(grpc.RpcError):
        run_async(post_service.GetPost(req, ctx))

    assert ctx._aborted is True
    assert ctx._code == grpc.StatusCode.NOT_FOUND
    assert "Post not found" in ctx._details


def test_create_comment_for_post(db_session_post: Session, post_service):
    post = create_post_util(
        db=db_session_post,
        title="Пост для комментов",
        description="Тест описания",
        user_id="author1",
        private=False,
        tags=[]
    )
    assert post.id == 1

    req = posts_pb2.CreateCommentRequest(
        post_id=post.id,
        user_id="user99",
        text="Комментарий"
    )
    ctx = FakeContext()

    returned_comment = run_async(post_service.CreateComment(req, ctx))

    assert returned_comment.id == 1
    assert returned_comment.post_id == post.id
    assert returned_comment.user_id == "user99"
    assert returned_comment.text == "Комментарий"
    assert returned_comment.created_at

    db_session_post.expire_all()
    comment_in_db: Comment = db_session_post.query(Comment).filter(Comment.id == returned_comment.id).first()
    assert comment_in_db is not None
    assert comment_in_db.text == "Комментарий"
    assert comment_in_db.post_id == post.id
    assert comment_in_db.user_id == "user99"
