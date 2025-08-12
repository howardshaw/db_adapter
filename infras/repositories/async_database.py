from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import QueuePool

from config import Settings
from .async_session import AsyncSession


class ASyncDatabase:
    def __init__(self, settings: Settings) -> None:
        self._engine = create_async_engine(
            settings.DB_URL_ASYNC,
            echo=settings.ECHO,
            poolclass=QueuePool,
            pool_pre_ping=True,
            pool_size=settings.POOL_SIZE,
            pool_recycle=settings.POOL_RECYCLE,
            max_overflow=settings.MAX_OVERFLOW,
            pool_timeout=settings.POOL_TIMEOUT,
        )
        self.session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    def get_session(self) -> AsyncSession:
        session = self.session_factory()
        return session
