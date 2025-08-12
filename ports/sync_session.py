from abc import ABC, abstractmethod
from typing import Any, Sequence, TypeVar


class ISyncSession(ABC):
    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def merge(self, instance: Any, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def flush(self, objects: Sequence[Any] | None = None) -> None:
        ...

    @abstractmethod
    def delete(self, instance: Any) -> None:
        ...


S = TypeVar('S', bound=ISyncSession)
SyncS = TypeVar('SyncS', bound=ISyncSession)

class ISyncExecutionStrategy(ABC):
    @abstractmethod
    def execute(self, session, stmt) -> Any: ...

    @abstractmethod
    def flush(self, session) -> None: ...

    @abstractmethod
    def refresh(self, session, instance: Any) -> None: ...

    @abstractmethod
    def delete(self, session, instance: Any) -> None: ...

    @abstractmethod
    def add(self, session, instance: Any) -> None: ...

    @abstractmethod
    def add_all(self, session, instances: list[Any]) -> None: ...

    @abstractmethod
    def merge(self, session, instance: Any) -> Any: ...

