import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    USER_SERVICE_URL: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        extra="ignore"
    )


settings = Settings()

USER_SERVICE_URL = settings.USER_SERVICE_URL
