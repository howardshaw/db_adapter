from contextlib import contextmanager
from typing import Generator, Callable

from asgiref.sync import async_to_sync,sync_to_async
from sqlalchemy.orm import sessionmaker

from ports.async_transaction import IAsyncTransactionManager
from ports.sync_transaction import ISyncTransactionManager
from repositories import T
from .async_session import AsyncSession
from .base_transaction import BaseTransactionManager
from .sync_session import SyncSession


class SyncTransactionManager(ISyncTransactionManager[SyncSession], BaseTransactionManager):
    def __init__(self, session_factory: sessionmaker):
        super().__init__(SyncSession)
        self._session_factory = session_factory
        self.logger.info(f"init sync transaction manager")

    @property
    def session_factory(self) -> Callable[[], SyncSession]:
        return self._session_factory

    @contextmanager
    def session(self) -> Generator[SyncSession, None, None]:
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

    @contextmanager
    def transaction(self) -> Generator[SyncSession, None, None]:
        session = self._session_factory()
        try:
            with session.begin():
                yield session
        finally:
            session.close()

    def execute_with_session(self, operation: Callable[[SyncSession], T]) -> T:
        """
        Execute a synchronous operation with session
        
        Args:
            operation: A callable that takes a session and returns a result
            
        Returns:
            The result of the operation
            
        Example:
            # Define your operation
            def get_user_by_id(session: Session) -> User:
                return session.query(User).filter(User.id == user_id).first()
            
            # Execute it
            user = transaction_manager.execute_with_session(get_user_by_id)
        """
        with self.session() as session:
            return operation(session)

    def execute_with_transaction(self, operation: Callable[[SyncSession], T]) -> T:
        """
        Execute a synchronous operation with transaction
        
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
            user = transaction_manager.execute_with_transaction(create_user)
        """
        with self.transaction() as session:
            return operation(session)

    def transactional(self, read_only: bool = False):
        """Returns a decorator for sync functions."""
        return self._create_transactional_decorator(read_only=read_only, is_async=False)


class AsyncToSyncTransactionManager(ISyncTransactionManager[AsyncSession], BaseTransactionManager):
    def __init__(self, async_transaction_manager: IAsyncTransactionManager[AsyncSession]):
        super().__init__(AsyncSession)
        self._async_transaction_manager = async_transaction_manager
        self.logger.info(f"init async to sync transaction manager")

    @property
    def session_factory(self) -> Callable[[], AsyncSession]:
        return self._async_transaction_manager.session_factory

    @contextmanager
    def session(self) -> Generator[AsyncSession, None, None]:
        raise NotImplementedError("Direct session context manager not supported for AsyncToSyncTransactionManager")

    @contextmanager
    def transaction(self) -> Generator[AsyncSession, None, None]:
        raise NotImplementedError("Direct transaction context manager not supported for AsyncToSyncTransactionManager")

    def execute_with_session(self, operation: Callable[[AsyncSession], T]) -> T:
        """
        Execute an operation with session using async_to_sync
        
        Args:
            operation: A callable that takes a session and returns a result
            
        Returns:
            The result of the operation
        """

        async def async_operation():
            async with self._async_transaction_manager.session() as session:
                return await sync_to_async(operation)(session)

        return async_to_sync(async_operation)()

    def execute_with_transaction(self, operation: Callable[[AsyncSession], T]) -> T:
        """
        Execute an operation with transaction using async_to_sync
        
        Args:
            operation: A callable that takes a session and returns a result
            
        Returns:
            The result of the operation
        """

        async def async_operation():
            async with self._async_transaction_manager.transaction() as session:
                return await sync_to_async(operation)(session)

        return async_to_sync(async_operation)()

    def transactional(self, read_only: bool = False):
        """Returns a decorator for sync functions."""
        return self._create_transactional_decorator(read_only=read_only, is_async=False)
