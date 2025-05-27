import os

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: str
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str

    KAFKA_BOOTSTRAP_SERVERS: str

    STATS_SERVER_PORT: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", ".env"),
        extra="ignore"
    )


settings = Settings()