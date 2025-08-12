from abc import ABC, abstractmethod
from typing import Any, Sequence, TypeVar


class IAsyncSession(ABC):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def execute(self, statement: Any, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    async def merge(self, instance: Any, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    async def flush(self, objects: Sequence[Any] | None = None) -> None: ...

    @abstractmethod
    async def delete(self, instance: Any) -> None: ...


S = TypeVar('S', bound=IAsyncSession)


