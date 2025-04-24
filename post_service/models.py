from __future__ import annotations

import datetime
from sqlalchemy import Integer, String, DateTime, func, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship
from google.protobuf.timestamp_pb2 import Timestamp
from pydantic import BaseModel

Base = declarative_base()

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    post = relationship("Post", back_populates="comments")

class CommentSchema(BaseModel):
    id: int
    post_id: int
    user_id: str
    text: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

    def to_grpc_dict(self) -> dict:
        def dt_to_timestamp(dt: datetime) -> dict:
            return dt.isoformat() + "Z"
        d = self.dict()
        d["created_at"] = dt_to_timestamp(self.created_at)
        return d


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    private: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=datetime.datetime.utcnow)

    comments = relationship("Comment", back_populates="post")

class PostSchema(BaseModel):
    id: int
    title: str
    description: str | None
    user_id: str
    private: bool
    tags: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

    def to_grpc_dict(self) -> dict:
        def dt_to_timestamp(dt: datetime) -> dict:
            return dt.isoformat() + "Z"
        d = self.dict()
        d["updated_at"] = dt_to_timestamp(self.updated_at)
        d["created_at"] = dt_to_timestamp(self.created_at)
        d["tags"] = self.tags.split(",") if self.tags else []
        return d
