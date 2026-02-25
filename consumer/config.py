from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

import logging
import logging.config
import json
from datetime import datetime


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        
        extra="ignore",
        env_prefix="EVENT_HANDLER_SERVICE_"
    )
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = Field(default=5432, ge=1, le=65535)
    POSTGRES_OUT_PORT: int = Field(default=1234, ge=1, le=65535)
    
    KAFKA_HOST: str
    KAFKA_PORT: int = Field(default=9092, ge=1, le=65535)
    TOPIC_NAME: str
    
    DEBUG: bool = False
    IS_DOCKER: bool = False

    @computed_field
    @property
    def ALEMBIC_DATABASE_URL(self) -> str:
        return self.ASYNC_DATABASE_URL if self.IS_DOCKER else self.LOCAL_DATABASE_URL
    
    @computed_field
    @property
    def LOCAL_DATABASE_SYNC_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}"
            f"@localhost:{self.POSTGRES_OUT_PORT}/{self.POSTGRES_DB}"
        )
    @computed_field
    @property
    def LOCAL_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}"
            f"@localhost:{self.POSTGRES_OUT_PORT}/{self.POSTGRES_DB}"
        )
    
    @computed_field
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        
    @computed_field
    @property
    def KAFKA_URL(self) -> str:
        return f"{self.KAFKA_HOST}:{self.KAFKA_PORT}"



class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "event_data"):
            event_data: dict[str, object] = getattr(record, "event_data")
            log_record.update(event_data)

        return json.dumps(log_record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        },
        "json": {
            "()": JsonFormatter,
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "/app/logs/events_consumer.log",
            "maxBytes": 10_000_000,
            "backupCount": 3,
            "encoding": "utf-8",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

settings = Settings()  # type: ignore[call-arg]


