import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str
    ALGORITHM: str

    KAFKA_BOOTSTRAP_SERVERS: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        extra="ignore"
    )


settings = Settings()


DATABASE_URL = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@" \
               f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
TEST_DATABASE_URL = "sqlite:////tmp/test_db.sqlite"


with open(settings.PRIVATE_KEY_PATH, "r") as file:
    private_key = file.read()

with open(settings.PUBLIC_KEY_PATH, "r") as file:
    public_key = file.read()


def get_auth_data():
    return {"private_key": private_key, "public_key": public_key, "algorithm": settings.ALGORITHM}
