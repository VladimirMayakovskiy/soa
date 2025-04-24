from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from post_service.config import DATABASE_URL
from post_service.models import Base

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
