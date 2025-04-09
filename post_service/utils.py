from __future__ import annotations

from sqlalchemy.orm import Session
from post_service.models import Post
from datetime import datetime


def create_post(db: Session, title: str, description: str, creator_id: str, private: bool, tags: list):
    tags_str = ",".join(tags) if tags else ""
    post = Post(title=title, description=description, creator_id=creator_id, private=private, tags=tags_str)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()


def update_post(
        db: Session,
        post_id: int,
        title: str | None = None,
        description: str | None = None,
        private: bool | None = None,
        tags: list | None = None,
):
    post = get_post(db, post_id)
    if not post:
        return None
    if title is not None:
        post.title = title
    if description is not None:
        post.description = description
    if private is not None:
        post.private = private
    if tags is not None:
        post.tags = ",".join(tags)

    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int):
    post = get_post(db, post_id)
    if post:
        db.delete(post)
        db.commit()


def list_posts(db: Session, page: int, limit: int):
    offset = (page - 1) * limit
    query = db.query(Post)
    return query.offset(offset).limit(limit).all(), query.count()
