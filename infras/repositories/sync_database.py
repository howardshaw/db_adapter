from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from config import Settings
from .sync_session import SyncSession


class SyncDatabase:
    def __init__(self, settings: Settings) -> None:
        self._engine = create_engine(
            settings.DB_URL_SYNC,
            echo=settings.ECHO,
            poolclass=QueuePool,
            pool_pre_ping=True,
            pool_size=settings.POOL_SIZE,
            pool_recycle=settings.POOL_RECYCLE,
            max_overflow=settings.MAX_OVERFLOW,
            pool_timeout=settings.POOL_TIMEOUT,
        )
        self.session_factory = sessionmaker(
            bind=self._engine,
            class_=SyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    def get_session(self) -> SyncSession:
        session = self.session_factory()
        return session
