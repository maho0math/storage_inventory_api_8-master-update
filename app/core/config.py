import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    MONGO_URI: str 

    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str
    CACHE_TTL_DEFAULT: int = 300

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    MINIO_USE_SSL: bool = False
    MAX_FILE_SIZE: int = 10485760  # 10 MB

    PROJECT_NAME: str = "Storage Inventory API"
    VERSION: str = "1.0.0"
    APP_ENV: str = "development"

    JWT_ACCESS_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str
    YANDEX_REDIRECT_URI: str = "http://localhost:8000/api/v1/yandex/callback"

    JWT_REFRESH_SECRET: str
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # RabbitMQ Settings (Lab 8)
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672

    # SMTP Settings (Lab 8)
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: str
    
    @field_validator(
        "DB_USER", "DB_PASSWORD", "DB_NAME", "MONGO_URI",
        "JWT_ACCESS_SECRET", "REDIS_HOST", "REDIS_PASSWORD",
        "YANDEX_CLIENT_ID", "YANDEX_CLIENT_SECRET",
        "MINIO_ENDPOINT", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY", "MINIO_BUCKET", 
        "RABBITMQ_USER", "RABBITMQ_PASS", "RABBITMQ_HOST",
        "SMTP_HOST", "SMTP_USER", "SMTP_PASS", "SMTP_FROM",
        mode="before"
    )
    @classmethod
    def strip_spaces(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        extra='ignore'
    )

    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    # Property to construct RabbitMQ connection URL
    @property
    def RABBITMQ_URL(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
    
    @property
    def SHOW_DOCS(self) -> bool:
        return self.APP_ENV.lower() == "development"

    @property
    def DOCS_URL(self) -> Optional[str]:
        return "/api/docs" if self.SHOW_DOCS else None

    @property
    def OPENAPI_URL(self) -> Optional[str]:
        return "/api/openapi.json" if self.SHOW_DOCS else None

settings = Settings()