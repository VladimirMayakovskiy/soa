import datetime
import grpc
from proto import posts_pb2, posts_pb2_grpc
from sqlalchemy.orm import Session
import post_service.db as db
from google.protobuf.json_format import ParseDict
from post_service.models import PostSchema, CommentSchema, Post, Comment
from google.protobuf.empty_pb2 import Empty
import post_service.utils as utils
from post_service.kafka_client import get_producer

def convert_comment(comment: Comment):
    return ParseDict(CommentSchema.model_validate(comment).to_grpc_dict(), posts_pb2.Comment(), ignore_unknown_fields=True)

def convert_post(post: Post):
    return ParseDict(PostSchema.model_validate(post).to_grpc_dict(), posts_pb2.Post(), ignore_unknown_fields=True)


class PostService(posts_pb2_grpc.PostServiceServicer):
    async def CreatePost(self, request, context):
        with next(db.get_db()) as session:
            post = utils.create_post(
                db=session,
                title=request.title,
                description=request.description,
                user_id=request.user_id,
                private=request.private,
                tags=list(request.tags)
            )
            return convert_post(post)

    async def GetPost(self, request, context):
        with next(db.get_db()) as session:
            post = get_post(
                db=session,
                post_id=request.id,
                user_id=request.user_id,
            )
            if post is None:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
            return convert_post(post)

    async def UpdatePost(self, request, context):
        with next(db.get_db()) as session:
            post = update_post(
                db=session,
                post_id=request.id,
                title=request.title,
                description=request.description,
                private=request.private,
                tags=list(request.tags),
                user_id=request.user_id,
            )
            if post is None:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
            return convert_post(post)

    async def DeletePost(self, request, context):
        with next(db.get_db()) as session:
            if not delete_post(db=session, post_id=request.id, user_id=request.user_id):
                await context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
            return Empty()

    async def ListPosts(self, request, context):
        with next(db.get_db()) as session:
            posts, total = list_posts(db=session, page=request.page, limit=request.limit, user_id=request.user_id)
            posts_msgs = [convert_post(post) for post in posts]
            return posts_pb2.ListPostsResponse(post=posts_msgs, total=total)

    async def ViewPost(self, request, context):
        await get_producer().send_event("views", {
            "post_id": request.id,
            "user_id": request.user_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        })
        return Empty()

    async def LikePost(self, request, context):
        await get_producer().send_event("likes", {
            "post_id": request.id,
            "user_id": request.user_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        })
        return Empty()

    async def CreateComment(self, request, context):
        with next(db.get_db()) as session:
            comment = utils.create_comment(
                db=session,
                post_id=request.post_id,
                user_id=request.user_id,
                text=request.text
            )
            await get_producer().send_event("comments", {
                "id": comment.id,
                "post_id": comment.post_id,
                "user_id": comment.user_id,
                "timestamp": comment.created_at.isoformat() + "Z"
            })

            return convert_comment(comment)

    async def ListComments(self, request, context):
        with next(db.get_db()) as session:
            comments, total = list_comments(db=session, post_id=request.post_id, page=request.page, limit=request.limit, user_id=request.user_id)
            comments_msgs = [convert_comment(c) for c in comments]
            return posts_pb2.ListCommentsResponse(com=comments_msgs, total=total)

def list_comments(db: Session, post_id: int, page: int, limit: int, user_id: str):
    if get_post(db, post_id, user_id) is None:
        return None
    comments, total = utils.list_comments(db, post_id, page, limit)
    return comments, total


def get_post(db: Session, post_id: int, user_id: str):
    post = utils.get_post(db, post_id)
    if post is None:
        return None

    if post.private and post.user_id != user_id:
        return None
    return post

def update_post(db: Session, post_id: int, title: str, description: str, private: bool, tags: list, user_id: str):
    post = utils.get_post(db, post_id)
    if post is None or post.user_id != user_id:
        return None
    return utils.update_post(db, post_id, title, description, private, tags)

def delete_post(db: Session, post_id: int, user_id: str):
    post = utils.get_post(db, post_id)
    if post is None or post.user_id != user_id:
        return None
    utils.delete_post(db, post_id)
    return True

def list_posts(db: Session, page: int, limit: int, user_id: str):
    posts, total = utils.list_posts(db, page, limit)
    posts = [p for p in posts if (not p.private) or (p.user_id == user_id)]
    return posts, total

