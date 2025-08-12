import logging
from typing import Any

from asgiref.sync import async_to_sync

from ports.sync_session_execution import ISyncExecutionStrategy
from .async_session import AsyncSession
from .sync_session import SyncSession

logger = logging.getLogger(__name__)


class SyncExecutionStrategy(ISyncExecutionStrategy):
    def execute(self, session: SyncSession, stmt: Any) -> Any:
        logger.info(f"execute sync stmt: {stmt}")
        return session.execute(stmt)

    def flush(self, session: SyncSession) -> None:
        logger.info(f"flush sync session")
        session.flush()

    def refresh(self, session: SyncSession, instance: Any) -> None:
        logger.info(f"refresh sync instance")
        session.refresh(instance)

    def delete(self, session: SyncSession, instance: Any) -> None:
        logger.info(f"delete sync instance")
        session.delete(instance)

    def add(self, session: SyncSession, instance: Any) -> None:
        logger.info(f"add sync instance")
        session.add(instance)

    def add_all(self, session: SyncSession, instances: list[Any]) -> None:
        logger.info(f"add_all sync instances")
        session.add_all(instances)

    def merge(self, session: SyncSession, instance: Any) -> Any:
        logger.info(f"merge sync instance")
        return session.merge(instance)


class AsyncToSyncExecutionStrategy(ISyncExecutionStrategy):
    def execute(self, session: AsyncSession, stmt: Any) -> Any:
        logger.info(f"execute async to sync stmt: {stmt}")
        return async_to_sync(session.execute)(stmt)

    def flush(self, session: AsyncSession) -> None:
        logger.info(f"flush async to sync session")
        async_to_sync(session.flush)()

    def refresh(self, session: AsyncSession, instance: Any) -> None:
        logger.info(f"refresh async to sync instance")
        async_to_sync(session.refresh)(instance)

    def delete(self, session: AsyncSession, instance: Any) -> None:
        logger.info(f"delete async to sync instance")
        async_to_sync(session.delete)(instance)

    def add(self, session: AsyncSession, instance: Any) -> None:
        logger.info(f"add async to sync instance")
        session.add(instance)

    def add_all(self, session: AsyncSession, instances: list[Any]) -> None:
        logger.info(f"add_all async to sync instances")
        session.add_all(instances)

    def merge(self, session: AsyncSession, instance: Any) -> Any:
        logger.info(f"merge async to sync instance")
        return async_to_sync(session.merge)(instance)
