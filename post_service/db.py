import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from post_service.config import DATABASE_URL as DATABASE_URL_, TEST_DATABASE_URL
from post_service.models import Base


if os.getenv("TEST", "false") == "true" and TEST_DATABASE_URL is not None:
    DATABASE_URL = TEST_DATABASE_URL
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    DATABASE_URL = DATABASE_URL_
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
