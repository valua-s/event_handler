from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


settings = Settings()  # type: ignore[call-arg]
