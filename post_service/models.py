from __future__ import annotations

import datetime
from sqlalchemy import Integer, String, DateTime, func, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from google.protobuf.timestamp_pb2 import Timestamp
from pydantic import BaseModel

Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    creator_id: Mapped[str] = mapped_column(String, nullable=False)
    private: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=datetime.datetime.utcnow)


class PostSchema(BaseModel):
    id: int
    title: str
    description: str | None
    creator_id: str
    private: bool
    tags: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

    def to_grpc_dict(self) -> dict:
        def dt_to_timestamp(dt: datetime) -> dict:
            ts = Timestamp()
            ts.FromDatetime(dt)
            return dt.isoformat() + "Z"
        d = self.dict()
        d["updated_at"] = dt_to_timestamp(self.updated_at)
        d["created_at"] = dt_to_timestamp(self.created_at)
        d["tags"] = self.tags.split(",") if self.tags else []
        return d
