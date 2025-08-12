from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Generic, Callable, Coroutine, Any


from repositories import T,TSession


class ISyncTransactionManager(Generic[TSession], ABC):
    @property
    @abstractmethod
    def session_factory(self) -> Callable[[], TSession]: ...

    @abstractmethod
    def session(self) -> AbstractContextManager[TSession]: ...

    @abstractmethod
    def transaction(self) -> AbstractContextManager[TSession]: ...

    @abstractmethod
    def execute_with_session(self, operation: Callable[[TSession], T]) -> T: ...

    @abstractmethod
    def execute_with_transaction(self, operation: Callable[[TSession], T]) -> T: ...

    @abstractmethod
    def transactional(self, read_only: bool = False) -> Callable:...