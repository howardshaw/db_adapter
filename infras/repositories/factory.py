from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Union
import logging

from asgiref.sync import sync_to_async, async_to_sync
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from config import Settings
from .async_session import AsyncSession

logger = logging.getLogger(__name__)


def get_engine(settings: Settings) -> Union[Engine, AsyncEngine]:
    if settings.USE_ASYNC_DB:
        logger.info(f"Using async db engine: {settings.DB_URL_ASYNC}")
        engine = create_async_engine(
            settings.DB_URL_ASYNC,
            echo=settings.ECHO,
            pool_pre_ping=True,
            pool_size=settings.POOL_SIZE,
            pool_recycle=settings.POOL_RECYCLE,
            max_overflow=settings.MAX_OVERFLOW,
            pool_timeout=settings.POOL_TIMEOUT,
            future=True,
        )
    else:
        logger.info(f"Using sync db engine: {settings.DB_URL_SYNC}")
        engine = create_engine(
            settings.DB_URL_SYNC,
            echo=settings.ECHO,
            poolclass=QueuePool,
            pool_pre_ping=True,
            pool_size=settings.POOL_SIZE,
            pool_recycle=settings.POOL_RECYCLE,
            max_overflow=settings.MAX_OVERFLOW,
            pool_timeout=settings.POOL_TIMEOUT,
            future=True,
        )
        
        # 添加连接池事件监听器
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            logger.debug(f"Connection checked out. Pool size: {engine.pool.size()}, Checked out: {engine.pool.checkedout()}")

        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            logger.debug(f"Connection checked in. Pool size: {engine.pool.size()}, Checked out: {engine.pool.checkedout()}")

        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            logger.debug("New database connection created")

        @event.listens_for(engine, "close")
        def receive_close(dbapi_connection):
            logger.debug("Database connection closed")
    
    return engine


def sync_session_factory(settings: Settings) -> sessionmaker:
    # For uniform_sync_db, we need to use the sync engine regardless of USE_ASYNC_DB
    if settings.REPO_DRIVER == 'uniform_sync_db':
        # Force sync engine for uniform_sync_db
        engine = create_engine(
            settings.DB_URL_SYNC,
            echo=settings.ECHO,
            poolclass=QueuePool,
            pool_pre_ping=True,
            pool_size=settings.POOL_SIZE,
            pool_recycle=settings.POOL_RECYCLE,
            max_overflow=settings.MAX_OVERFLOW,
            pool_timeout=settings.POOL_TIMEOUT,
            future=True,
        )
    else:
        # Use the normal engine selection logic
        engine = get_engine(settings)
    
    return sessionmaker(
        bind=engine,
        # 优化 session 配置
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        future=True,
    )


def async_session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    # For uniform_async_db, we need to use the async engine regardless of USE_ASYNC_DB
    if settings.REPO_DRIVER == 'uniform_async_db':
        # Force async engine for uniform_async_db
        engine = create_async_engine(
            settings.DB_URL_ASYNC,
            echo=settings.ECHO,
            pool_pre_ping=True,
            pool_size=settings.POOL_SIZE,
            pool_recycle=settings.POOL_RECYCLE,
            max_overflow=settings.MAX_OVERFLOW,
            pool_timeout=settings.POOL_TIMEOUT,
            future=True,
        )
    else:
        # Use the normal engine selection logic
        engine = get_engine(settings)
    
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
        autoflush=False,
    )


def get_session_factory(settings: Settings) -> Union[sessionmaker, async_sessionmaker[AsyncSession]]:
    engine = get_engine(settings)
    if settings.USE_ASYNC_DB:
        return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    else:
        return sessionmaker(bind=engine)


async def get_db_session(settings: Settings) -> AsyncGenerator[Union[AsyncSession, Session], None]:
    factory = get_session_factory(settings)
    if settings.USE_ASYNC_DB:
        async with factory() as session:
            yield session
    else:
        def _open_session() -> Session:
            return factory()

        session = await sync_to_async(_open_session, thread_sensitive=True)()

        try:
            yield session
        finally:
            await sync_to_async(session.close, thread_sensitive=True)()


def get_db_session_sync(settings: Settings) -> Generator[Union[AsyncSession, Session], None, None]:
    factory = get_session_factory(settings)
    if not settings.USE_ASYNC_DB:
        session: Session = factory()
        try:
            yield session
        finally:
            session.close()
    else:
        async def _open_async_session() -> AsyncSession:
            async with factory() as session:
                return session

        async def close_async_session(session: AsyncSession) -> None:
            await session.close()

        session: AsyncSession = async_to_sync(_open_async_session)()
        try:
            yield session
        finally:
            async_to_sync(close_async_session)(session)


@asynccontextmanager
async def db_session_context(settings: Settings) -> AsyncGenerator[Union[AsyncSession, Session], None]:
    factory = get_session_factory(settings)
    if settings.USE_ASYNC_DB:
        async with factory() as session:
            yield session
    else:
        def _open_session() -> Session:
            return factory()

        session: Session = await sync_to_async(_open_session, thread_sensitive=True)()
        try:
            yield session
        finally:
            await sync_to_async(session.close, thread_sensitive=True)()


@contextmanager
def db_session_context_sync(settings: Settings) -> Generator[Union[AsyncSession, Session], None, None]:
    factory = get_session_factory(settings)

    if not settings.USE_ASYNC_DB:
        session = factory()
        try:
            yield session
        finally:
            session.close()
    else:
        async def open_async_session() -> AsyncSession:
            async with factory() as session:
                return session

        async def close_async_session(session: AsyncSession) -> None:
            await session.close()

        session: AsyncSession = async_to_sync(open_async_session)()
        try:
            yield session
        finally:
            async_to_sync(close_async_session)(session)
