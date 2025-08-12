from abc import abstractmethod, ABC
from typing import Any

from repositories import TSession


class ISyncExecutionStrategy(ABC):
    @abstractmethod
    def execute(self, session: TSession, stmt: Any) -> Any: ...

    @abstractmethod
    def flush(self, session: TSession) -> None: ...

    @abstractmethod
    def refresh(self, session: TSession, instance: Any) -> None: ...

    @abstractmethod
    def delete(self, session: TSession, instance: Any) -> None: ...

    @abstractmethod
    def add(self, session: TSession, instance: Any) -> None: ...

    @abstractmethod
    def add_all(self, session: TSession, instances: list[Any]) -> None: ...

    @abstractmethod
    def merge(self, session: TSession, instance: Any) -> Any: ...
