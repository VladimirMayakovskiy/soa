import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POST_DB_HOST: str
    POST_DB_PORT: int
    POST_DB_NAME: str
    POST_DB_USER: str
    POST_DB_PASSWORD: str
    POST_SERVER_PORT: str
    POST_SERVER_ADDR: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", ".env"),
        extra="ignore"
    )


settings = Settings()


DATABASE_URL = f"postgresql+psycopg2://{settings.POST_DB_USER}:{settings.POST_DB_PASSWORD}@" \
               f"{settings.POST_DB_HOST}:{settings.POST_DB_PORT}/{settings.POST_DB_NAME}"
