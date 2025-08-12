from abc import ABC, abstractmethod
from typing import Generic, AsyncContextManager, Callable, Awaitable

from repositories import T, TSession

AsyncOperation = Callable[[TSession], Awaitable[T]]


class IAsyncTransactionManager(ABC, Generic[TSession]):
    @property
    @abstractmethod
    def session_factory(self) -> Callable[[], TSession]: ...

    @abstractmethod
    def session(self) -> AsyncContextManager[TSession]: ...

    @abstractmethod
    def transaction(self) -> AsyncContextManager[TSession]: ...

    @abstractmethod
    async def execute_with_session(self, operation: AsyncOperation[TSession, T]) -> T: ...

    @abstractmethod
    async def execute_with_transaction(self, operation: AsyncOperation[TSession, T]) -> T: ...

    @abstractmethod
    def transactional(self, read_only: bool = False) -> Callable: ...
