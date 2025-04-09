import grpc
from proto import posts_pb2, posts_pb2_grpc
from sqlalchemy.orm import Session
import post_service.db as db
from google.protobuf.json_format import ParseDict
from post_service.config import settings
from post_service.models import PostSchema
from google.protobuf.empty_pb2 import Empty
import post_service.utils as utils
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)


class PostService(posts_pb2_grpc.PostServiceServicer):
    async def CreatePost(self, request, context):
        with next(db.get_db()) as session:
            post = create_post(
                db=session,
                title=request.title,
                description=request.description,
                creator_id=request.user_id,
                private=request.private,
                tags=list(request.tags)
            )
            return ParseDict(PostSchema.model_validate(post).to_grpc_dict(), posts_pb2.Post(), ignore_unknown_fields=True)

    async def GetPost(self, request, context):
        with next(db.get_db()) as session:
            post = get_post(
                db=session,
                post_id=request.id,
                user_id=request.user_id,
            )
            if post is None:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
            return ParseDict(PostSchema.model_validate(post).to_grpc_dict(), posts_pb2.Post(), ignore_unknown_fields=True)

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
            return ParseDict(PostSchema.model_validate(post).to_grpc_dict(), posts_pb2.Post(), ignore_unknown_fields=True)

    async def DeletePost(self, request, context):
        with next(db.get_db()) as session:
            if not delete_post(db=session, post_id=request.id, user_id=request.user_id):
                await context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
            return Empty()

    async def ListPosts(self, request, context):
        with next(db.get_db()) as session:
            posts, total = list_posts(db=session, page=request.page, limit=request.limit, user_id=request.user_id)
            posts_msgs = [ParseDict(PostSchema.model_validate(post).to_grpc_dict(), posts_pb2.Post(), ignore_unknown_fields=True) for post in posts]
            return posts_pb2.ListPostsResponse(post=posts_msgs, total=total)


def create_post(db: Session, title: str, description: str, creator_id: str, private: bool, tags: list):
    return utils.create_post(db, title, description, creator_id, private, tags)

def get_post(db: Session, post_id: int, user_id: str):
    post = utils.get_post(db, post_id)
    if post is None:
        return None

    if post.private and post.creator_id != user_id:
        return None
    return post

def update_post(db: Session, post_id: int, title: str, description: str, private: bool, tags: list, user_id: str):
    post = utils.get_post(db, post_id)
    if post is None or post.creator_id != user_id:
        return None
    return utils.update_post(db, post_id, title, description, private, tags)

def delete_post(db: Session, post_id: int, user_id: str):
    post = utils.get_post(db, post_id)
    if post is None or post.creator_id != user_id:
        return None
    utils.delete_post(db, post_id)
    return True

def list_posts(db: Session, page: int, limit: int, user_id: str):
    posts, total = utils.list_posts(db, page, limit)
    posts = [p for p in posts if (not p.private) or (p.creator_id == user_id)]
    return posts, total


async def serve():
    server = grpc.aio.server()
    posts_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    listen_addr = f"[::]:{settings.POST_SERVER_PORT}" #51075
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())

