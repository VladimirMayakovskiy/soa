import os
import httpx
from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    USER_SERVICE_URL: str
    POST_SERVER_PORT: str
    POST_SERVER_ADDR: str

    STATS_SERVER_PORT: str
    STATS_SERVER_ADDR: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        extra="ignore"
    )


settings = Settings()

USER_SERVICE_URL = settings.USER_SERVICE_URL

public_key: str = None
algorithms: str = None


async def fetch_user_service_data():
    global public_key, algorithms
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{USER_SERVICE_URL}/public_key')
        print("FETCH")
        if response.status_code != 200:
            raise RuntimeError("")

        data = response.json()
        public_key = data.get('public_key')
        algorithms = data.get('algorithm')

        print(public_key, algorithms)


def get_public_key() -> str:
    return public_key


def get_algorithms() -> str:
    return algorithms


def setup_user_service_data(app: FastAPI):
    @app.on_event("startup")
    async def _fetch_user_service_data():
        await fetch_user_service_data()
