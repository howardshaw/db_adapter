import logging
from typing import Any

from asgiref.sync import sync_to_async

from ports.async_session_execution import IAsyncExecutionStrategy
from .async_session import AsyncSession
from .sync_session import SyncSession

logger = logging.getLogger(__name__)


class AsyncExecutionStrategy(IAsyncExecutionStrategy):
    async def execute(self, session: AsyncSession, stmt: Any) -> Any:
        logger.info(f"execute async stmt: {stmt}")
        return await session.execute(stmt)

    async def flush(self, session: AsyncSession) -> None:
        logger.info(f"flush async session")
        await session.flush()

    async def refresh(self, session: AsyncSession, instance: Any) -> None:
        logger.info(f"refresh async instance")
        await session.refresh(instance)

    async def delete(self, session: AsyncSession, instance: Any) -> None:
        logger.info(f"delete async instance")
        await session.delete(instance)

    def add(self, session: AsyncSession, instance: Any) -> None:
        logger.info(f"add async instance")
        session.add(instance)

    def add_all(self, session: AsyncSession, instances: list[Any]) -> None:
        logger.info(f"add_all async instances")
        session.add_all(instances)

    async def merge(self, session: AsyncSession, instance: Any) -> Any:
        logger.info(f"merge async instance")
        return await session.merge(instance)


class SyncToAsyncExecutionStrategy(IAsyncExecutionStrategy):
    async def execute(self, session: SyncSession, stmt) -> Any:
        logger.info(f"execute sync to async stmt: {stmt}")

        return await sync_to_async(session.execute, thread_sensitive=True)(stmt)

    async def flush(self, session: SyncSession) -> None:
        logger.info(f"flush sync to async session")
        await sync_to_async(session.flush, thread_sensitive=True)()

    async def refresh(self, session: SyncSession, instance: Any) -> None:
        logger.info(f"refresh sync to async instance")
        await sync_to_async(session.refresh, thread_sensitive=True)(instance)

    async def delete(self, session: SyncSession, instance: Any) -> None:
        logger.info(f"delete sync to async instance")
        await sync_to_async(session.delete, thread_sensitive=True)(instance)

    def add(self, session: SyncSession, instance: Any) -> None:
        logger.info(f"add sync to async instance")
        session.add(instance)

    def add_all(self, session: SyncSession, instances: list[Any]) -> None:
        logger.info(f"add_all sync to async instances")
        session.add_all(instances)

    async def merge(self, session: SyncSession, instance: Any) -> Any:
        logger.info(f"merge sync to async instance")
        return await sync_to_async(session.merge, thread_sensitive=True)(instance)
