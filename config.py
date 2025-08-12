from functools import lru_cache
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # DB
    USE_ASYNC_DB: Annotated[bool, Field(description="Whether use async db")] = True
    REPO_DRIVER: Annotated[str, Field(description="Repository driver: async_db, sync_db, uniform_async_db, or uniform_sync_db")] = "async_db"
    USE_ASYNC_ROUTER: Annotated[bool, Field(description="Whether use async router")] = True

    # DB connection
    DB_URL_SYNC: Annotated[str, Field(description="SYNC DB URL")] = "sqlite:///./example.db"
    DB_URL_ASYNC: Annotated[str, Field(description="Async DB URL")] = "sqlite+aiosqlite:///./example.db"


    # SQLAlchemy
    ECHO: Annotated[bool, Field(description="SQL Echo")] = False
    POOL_SIZE: Annotated[int, Field(description='Connection pool size', ge=1)] = 20
    MAX_OVERFLOW: Annotated[int, Field(description='Maximum overflow connections', ge=0)] = 10
    POOL_RECYCLE: Annotated[int, Field(description='Connection recycle time in seconds', ge=0)] = 10
    POOL_TIMEOUT: Annotated[int, Field(description='Connection timeout in seconds', ge=0)] = 5


@lru_cache
def get_settings() -> Settings:
    """Get application settings with .env file support."""
    import logging

    logger = logging.getLogger(__name__)


    try:
        settings = Settings()

        # Log configuration summary
        logger.info(f"Database type: {'Async' if settings.USE_ASYNC_DB else 'Sync'}")
        logger.info(f"Repository driver: {settings.REPO_DRIVER}")
        logger.info(f"Router type: {'Async' if settings.USE_ASYNC_ROUTER else 'Sync'}")
        logger.info(f"Pool size: {settings.POOL_SIZE}")
        logger.info(f"Max overflow: {settings.MAX_OVERFLOW}")

        return settings

    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise


settings = get_settings()
