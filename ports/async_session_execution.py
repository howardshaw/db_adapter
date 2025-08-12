from abc import abstractmethod, ABC
from typing import Any

from repositories import TSession


class IAsyncExecutionStrategy(ABC):
    @abstractmethod
    async def execute(self, session: TSession, stmt: Any) -> Any: ...

    @abstractmethod
    async def flush(self, session: TSession) -> None: ...

    @abstractmethod
    async def refresh(self, session: TSession, instance: Any) -> None: ...

    @abstractmethod
    async def delete(self, session: TSession, instance: Any) -> None: ...

    @abstractmethod
    def add(self, session: TSession, instance: Any) -> None: ...

    @abstractmethod
    def add_all(self, session: TSession, instances: list[Any]) -> None: ...

    @abstractmethod
    async def merge(self, session: TSession, instance: Any) -> Any: ...
