from contextlib import asynccontextmanager
from typing import Callable, AsyncGenerator

from asgiref.sync import sync_to_async
from sqlalchemy.ext.asyncio import async_sessionmaker

from ports.async_transaction import IAsyncTransactionManager, AsyncOperation
from ports.sync_transaction import ISyncTransactionManager
from repositories import T
from .async_session import AsyncSession
from .base_transaction import BaseTransactionManager
from .sync_session import SyncSession


class AsyncTransactionManager(IAsyncTransactionManager[AsyncSession], BaseTransactionManager):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(AsyncSession)
        self._session_factory = session_factory
        self.logger.info(f"init async transaction manager")

    @property
    def session_factory(self) -> Callable[[], AsyncSession]:
        return self._session_factory

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session = self._session_factory()
        try:
            yield session
        finally:
            await session.close()

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        session = self._session_factory()
        try:
            async with session.begin():
                yield session
        finally:
            await session.close()

    async def execute_with_session(self, operation: AsyncOperation[AsyncSession, T]) -> T:
        """
        Execute an asynchronous operation with session
        
        Args:
            operation: A callable that takes a session and returns a result
            
        Returns:
            The result of the operation
            
        Example:
            # Define your operation
            async def get_user_by_id(session: AsyncSession) -> User:
                result = await session.execute(select(User).where(User.id == user_id))
                return result.scalar_one()
            
            # Execute it
            user = await transaction_manager.execute_with_session(get_user_by_id)
        """
        async with self.session() as session:
            return await operation(session)

    async def execute_with_transaction(self, operation: AsyncOperation[AsyncSession, T]) -> T:
        """
        Execute an asynchronous operation with transaction
        
        Args:
            operation: A callable that takes a session and returns a result
            
        Returns:
            The result of the operation
            
        Example:
            # Define your operation
            async def create_user(session: AsyncSession) -> User:
                user = User(name="John", email="john@example.com")
                session.add(user)
                await session.flush()
                return user
            
            # Execute it with transaction
            user = await transaction_manager.execute_with_transaction(create_user)
        """
        async with self.transaction() as session:
            return await operation(session)

    def transactional(self, read_only: bool = False):
        """Returns a decorator for async functions."""
        return self._create_transactional_decorator(read_only=read_only, is_async=True)


class SyncToAsyncTransactionManager(IAsyncTransactionManager[SyncSession], BaseTransactionManager):
    def __init__(self, sync_transaction_manager: ISyncTransactionManager[SyncSession]):
        super().__init__(SyncSession)
        self._sync_transaction_manager = sync_transaction_manager
        self.logger.info(f"init sync to async transaction manager")

    @property
    def session_factory(self) -> Callable[[], SyncSession]:
        return self._sync_transaction_manager.session_factory

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[SyncSession, None]:
        sync_session = await sync_to_async(self._sync_transaction_manager.session_factory, thread_sensitive=True)()

        try:
            yield sync_session
        finally:
            await sync_to_async(sync_session.close, thread_sensitive=True)()

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[SyncSession, None]:
        sync_session = await sync_to_async(self._sync_transaction_manager.session_factory, thread_sensitive=True)()

        try:
            await sync_to_async(sync_session.begin, thread_sensitive=True)()
            yield sync_session
            await sync_to_async(sync_session.commit, thread_sensitive=True)()
        except Exception:
            await sync_to_async(sync_session.rollback, thread_sensitive=True)()
            raise
        finally:
            await sync_to_async(sync_session.close, thread_sensitive=True)()

    async def execute_with_session(self, operation: AsyncOperation[SyncSession, T]) -> T:
        """
        Execute a synchronous operation with session using asyncio.to_thread
        
        Args:
            operation: A callable that takes a session and returns a result
            
        Returns:
            The result of the operation
            
        Example:
            # Define your operation
            def get_user_by_id(session: Session) -> User:
                return session.query(User).filter(User.id == user_id).first()
            
            # Execute it
            user = await transaction_manager.execute_with_session(get_user_by_id)
        """

        sync_session = await sync_to_async(self._sync_transaction_manager.session_factory, thread_sensitive=True)()

        try:
            return await operation(sync_session)
        finally:
            await sync_to_async(sync_session.close, thread_sensitive=True)()

    async def execute_with_transaction(self, operation: AsyncOperation[SyncSession, T]) -> T:
        """
        Execute a synchronous operation with transaction using asyncio.to_thread
        
        Args:
            operation: A callable that takes a session and returns a result
            
        Returns:
            The result of the operation
            
        Example:
            # Define your operation
            def create_user(session: Session) -> User:
                user = User(name="John", email="john@example.com")
                session.add(user)
                return user
            
            # Execute it with transaction
            user = await transaction_manager.execute_with_transaction(create_user)
        """

        sync_session = await sync_to_async(self._sync_transaction_manager.session_factory, thread_sensitive=True)()

        try:
            await sync_to_async(sync_session.begin, thread_sensitive=True)()
            result = await operation(sync_session)
            await sync_to_async(sync_session.commit, thread_sensitive=True)()
            return result
        except Exception:
            await sync_to_async(sync_session.rollback, thread_sensitive=True)()
            raise
        finally:
            await sync_to_async(sync_session.close, thread_sensitive=True)()

    def transactional(self, read_only: bool = False):
        """Returns a decorator for async functions."""
        return self._create_transactional_decorator(read_only=read_only, is_async=True)
