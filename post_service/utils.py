from __future__ import annotations

from sqlalchemy.orm import Session
from post_service.models import Post, Comment
from datetime import datetime


def create_post(db: Session, title: str, description: str, user_id: str, private: bool, tags: list) -> Post:
    tags_str = ",".join(tags) if tags else ""
    post = Post(title=title, description=description, user_id=user_id, private=private, tags=tags_str)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_post(db: Session, post_id: int) -> Post:
    return db.query(Post).filter(Post.id == post_id).first()


def update_post(
        db: Session,
        post_id: int,
        title: str | None = None,
        description: str | None = None,
        private: bool | None = None,
        tags: list | None = None,
) -> Post:
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


def delete_post(db: Session, post_id: int) -> None:
    post = get_post(db, post_id)
    if post:
        db.delete(post)
        db.commit()


def list_posts(db: Session, page: int, limit: int) -> tuple[list[Post], int]:
    offset = (page - 1) * limit
    query = db.query(Post)
    return query.offset(offset).limit(limit).all(), query.count()


def create_comment(db: Session, post_id: int, user_id: str, text: str) -> Comment:
    comment = Comment(post_id=post_id, user_id=user_id, text=text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments(db: Session, post_id: int, page: int, limit: int) -> tuple[list[Comment], int]:
    offset = (page - 1) * limit
    query = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc())
    return query.offset(offset).limit(limit).all(), query.count()
